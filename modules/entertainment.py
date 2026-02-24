from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from modules.models import db, City, Theatre, Movie, Show, Event, SportsMatch, Booking, Rating, UserPreference
import uuid
import random
import json
import qrcode
from datetime import datetime, timedelta
import os
import base64
from io import BytesIO

entertainment_bp = Blueprint('entertainment', __name__)

# ============================================
# RECOMMENDATION ALGORITHM
# ============================================

def get_user_preferences(user_id):
    """Get user preferences for personalized recommendations"""
    pref = UserPreference.query.filter_by(user_id=user_id).first()
    if pref:
        return {
            'genres': json.loads(pref.preferred_genres) if pref.preferred_genres else [],
            'languages': json.loads(pref.preferred_languages) if pref.preferred_languages else [],
            'city': pref.preferred_city
        }
    return {'genres': [], 'languages': [], 'city': None}

def calculate_movie_score(movie, user_prefs):
    """Calculate recommendation score for a movie"""
    score = 0
    movie_genres = json.loads(movie.genre) if movie.genre else []
    movie_languages = json.loads(movie.language) if movie.language else []
    
    # Genre matching (40% weight)
    common_genres = set(movie_genres) & set(user_prefs['genres'])
    score += len(common_genres) * 40
    
    # Language matching (30% weight)
    if user_prefs['languages'] and movie_languages:
        if any(lang in movie_languages for lang in user_prefs['languages']):
            score += 30
    
    # Rating (20% weight)
    score += movie.rating * 4  # rating out of 5 = max 20
    
    # Recency (10% weight)
    days_since_release = (datetime.utcnow() - movie.release_date).days
    if days_since_release < 30:  # New release
        score += 10
    elif days_since_release < 90:  # Recent
        score += 5
    
    return min(score, 100)  # Normalize to 100

def get_recommendations(user_id, item_type='movie', limit=10):
    """Get personalized recommendations"""
    user_prefs = get_user_preferences(user_id)
    
    if item_type == 'movie':
        items = Movie.query.filter_by(is_active=True).all()
        scored_items = [(movie, calculate_movie_score(movie, user_prefs)) for movie in items]
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_items[:limit]]
    
    return []

# ============================================
# DYNAMIC PRICING ALGORITHM
# ============================================

def calculate_dynamic_price(base_price, show_time, show_date):
    """Calculate dynamic pricing based on demand factors"""
    price = base_price
    weekday = show_date.weekday()  # 0=Monday, 6=Sunday
    
    # Weekend surcharge (Fri-Sun)
    if weekday >= 4:  # Friday, Saturday, Sunday
        price *= 1.2
    
    # Evening shows premium
    hour = int(show_time.split(':')[0])
    if 'PM' in show_time and hour >= 6:  # 6 PM onwards
        price *= 1.15
    elif 'AM' in show_time and hour <= 11:  # Morning shows
        price *= 0.9  # Discount
    
    # Holiday surcharge (simplified)
    # In real app, check holiday database
    
    return round(price, 2)

# ============================================
# SEAT ALLOCATION ALGORITHM
# ============================================

def generate_seat_layout(rows=10, cols=12):
    """Generate initial seat layout"""
    layout = {}
    for row in range(rows):
        row_label = chr(65 + row)  # A, B, C, ...
        for col in range(1, cols + 1):
            seat_id = f"{row_label}{col}"
            layout[seat_id] = {
                'available': True,
                'type': 'normal',  # normal, vip, recliner
                'price_multiplier': 1.0
            }
    
    # VIP seats (last 2 rows, middle)
    for row in range(rows-2, rows):
        row_label = chr(65 + row)
        for col in range(4, 9):
            seat_id = f"{row_label}{col}"
            layout[seat_id]['type'] = 'vip'
            layout[seat_id]['price_multiplier'] = 1.5
    
    return layout

def get_available_seats(show_id):
    """Get available seats for a show"""
    show = Show.query.get(show_id)
    if not show:
        return []
    
    # Get booked seats from bookings
    bookings = Booking.query.filter_by(
        booking_type='movie',
        item_id=show_id,
        status='confirmed'
    ).all()
    
    booked_seats = []
    for booking in bookings:
        booked_seats.extend(json.loads(booking.seats))
    
    # Generate layout if not exists
    layout = json.loads(show.seat_layout) if show.seat_layout else generate_seat_layout()
    
    # Update availability
    for seat in booked_seats:
        if seat in layout:
            layout[seat]['available'] = False
    
    return layout

# ============================================
# ROUTES
# ============================================

@entertainment_bp.route('/entertainment')
def entertainment_home():
    """Entertainment Home Page"""
    # Get current playing movies
    movies = Movie.query.filter_by(is_active=True).order_by(Movie.release_date.desc()).limit(10).all()
    
    # Upcoming events
    events = Event.query.filter_by(is_active=True).filter(Event.event_date > datetime.utcnow()).limit(6).all()
    
    # Sports matches
    sports = SportsMatch.query.filter_by(is_active=True).filter(SportsMatch.match_date > datetime.utcnow()).limit(6).all()
    
    # Popular cities
    cities = City.query.filter_by(is_active=True).limit(5).all()
    
    return render_template('entertainment_home.html', 
                         movies=movies,
                         events=events,
                         sports=sports,
                         cities=cities)

@entertainment_bp.route('/entertainment/movies')
def movies_list():
    """List all movies with filters"""
    city = request.args.get('city')
    language = request.args.get('language')
    genre = request.args.get('genre')
    
    query = Movie.query.filter_by(is_active=True)
    
    if language:
        query = query.filter(Movie.language.contains(language))
    if genre:
        query = query.filter(Movie.genre.contains(genre))
    
    # Sort by release date (newest first)
    movies = query.order_by(Movie.release_date.desc()).all()
    
    # Get personalized recommendations for logged-in users
    recommendations = []
    if current_user.is_authenticated:
        recommendations = get_recommendations(current_user.id, 'movie', 5)
    
    languages = ['Hindi', 'English', 'Marathi', 'Tamil', 'Telugu', 'Bengali']
    genres = ['Action', 'Comedy', 'Drama', 'Romance', 'Thriller', 'Horror']
    
    return render_template('movies_list.html',
                         movies=movies,
                         recommendations=recommendations,
                         languages=languages,
                         genres=genres,
                         selected_language=language,
                         selected_genre=genre)

@entertainment_bp.route('/entertainment/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Get shows for this movie
    shows = Show.query.filter(
        Show.movie_id == movie_id,
        Show.is_active == True,
        Show.show_date >= datetime.utcnow().date()
    ).order_by(Show.show_date, Show.show_time).all()
    
    return render_template('movie_details.html', movie=movie, shows=shows)

    
    # Group shows by theatre
    shows_by_theatre = {}
    for show in shows:
        theatre = Theatre.query.get(show.theatre_id)
        if theatre:
            if theatre.id not in shows_by_theatre:
                shows_by_theatre[theatre.id] = {
                    'theatre': theatre,
                    'shows': []
                }
            shows_by_theatre[theatre.id]['shows'].append(show)
    
    return render_template('movie_details.html',
                         movie=movie,
                         shows_by_theatre=shows_by_theatre)

@entertainment_bp.route('/entertainment/show/<int:show_id>')
@login_required
def show_seats(show_id):
    """Show seat selection page"""
    show = Show.query.get_or_404(show_id)
    
    # Check if show is still available
    if show.show_date.date() < datetime.utcnow().date():
        flash('This show has already passed', 'error')
        return redirect(url_for('entertainment.movie_details', movie_id=show.movie_id))
    
    # Get available seats
    seats = get_available_seats(show_id)
    
    # Calculate dynamic price
    dynamic_price = calculate_dynamic_price(
        show.ticket_price,
        show.show_time,
        show.show_date
    )
    
    return render_template('seat_selection.html',
                         show=show,
                         seats=seats,
                         dynamic_price=dynamic_price)

@entertainment_bp.route('/entertainment/book', methods=['POST'])
@login_required
def book_tickets():
    """Book tickets"""
    data = request.json
    
    show_id = data.get('show_id')
    selected_seats = data.get('seats', [])
    payment_method = data.get('payment_method', 'UPI')
    
    show = Show.query.get_or_404(show_id)
    
    # Check availability again
    available_seats = get_available_seats(show_id)
    for seat in selected_seats:
        if seat not in available_seats or not available_seats[seat]['available']:
            return jsonify({'success': False, 'message': f'Seat {seat} is no longer available'})
    
    # Calculate total amount
    total_amount = 0
    for seat in selected_seats:
        multiplier = available_seats[seat]['price_multiplier']
        total_amount += show.ticket_price * multiplier
    
    # Apply dynamic pricing
    dynamic_price = calculate_dynamic_price(
        total_amount / len(selected_seats),  # average price
        show.show_time,
        show.show_date
    )
    total_amount = dynamic_price * len(selected_seats)
    
    # Generate transaction ID
    txn_id = f"BK{uuid.uuid4().hex[:12].upper()}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_data = f"Booking:{txn_id}\nShow:{show_id}\nSeats:{','.join(selected_seats)}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        booking_type='movie',
        item_id=show_id,
        seats=json.dumps(selected_seats),
        total_amount=total_amount,
        payment_method=payment_method,
        transaction_id=txn_id,
        qr_code=qr_base64,
        status='confirmed'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Update available seats in show (in real app, decrement)
    # show.available_seats -= len(selected_seats)
    
    return jsonify({
        'success': True,
        'booking_id': booking.id,
        'transaction_id': txn_id,
        'qr_code': qr_base64
    })

@entertainment_bp.route('/entertainment/booking/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    """Booking confirmation page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure booking belongs to current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('entertainment.entertainment_home'))
    
    return render_template('booking_confirmation.html', booking=booking)
@entertainment_bp.route('/entertainment/events')
def events_list():
    """Events listing page"""
    return render_template('events_list.html', events=[])

@entertainment_bp.route('/entertainment/sports')
def sports_list():
    """Sports listing page"""
    return render_template('sports_list.html', sports=[])

@entertainment_bp.route('/entertainment/my-bookings')
@login_required
def my_bookings():
    """User's booking history"""
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(Booking.booking_date.desc()).all()
    
    return render_template('my_bookings.html', bookings=bookings)
@entertainment_bp.route('/api/entertainment/prices')
def api_entertainment_prices():
    """API for live entertainment prices"""
    import random
    from datetime import datetime
    
    # Mock data for prices
    prices = {
        'movies': random.randint(150, 350),
        'events': random.randint(500, 2000),
        'sports': random.randint(300, 1500)
    }
    
    return jsonify({
        'success': True,
        'prices': prices,
        'timestamp': datetime.utcnow().isoformat()
    })

@entertainment_bp.route('/entertainment/rate', methods=['POST'])
@login_required
def rate_item():
    """Rate a movie/event/sports match"""
    item_type = request.form.get('item_type')
    item_id = request.form.get('item_id')
    rating = int(request.form.get('rating'))
    review = request.form.get('review', '')
    
    # Check if already rated
    existing = Rating.query.filter_by(
        user_id=current_user.id,
        item_type=item_type,
        item_id=item_id
    ).first()
    
    if existing:
        existing.rating = rating
        existing.review = review
    else:
        new_rating = Rating(
            user_id=current_user.id,
            item_type=item_type,
            item_id=item_id,
            rating=rating,
            review=review
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    # Update average rating for the item
    if item_type == 'movie':
        item = Movie.query.get(item_id)
    elif item_type == 'event':
        item = Event.query.get(item_id)
    else:
        item = SportsMatch.query.get(item_id)
    
    if item:
        ratings = Rating.query.filter_by(item_type=item_type, item_id=item_id).all()
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        item.rating = round(avg_rating, 1)
        item.total_ratings = len(ratings)
        db.session.commit()
    
    flash('Thank you for your rating!', 'success')
    return redirect(request.referrer)

@entertainment_bp.route('/entertainment/preferences', methods=['GET', 'POST'])
@login_required
def user_preferences():
    """User preferences for recommendations"""
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        languages = request.form.getlist('languages')
        city_id = request.form.get('city')
        
        pref = UserPreference.query.filter_by(user_id=current_user.id).first()
        if not pref:
            pref = UserPreference(user_id=current_user.id)
        
        pref.preferred_genres = json.dumps(genres)
        pref.preferred_languages = json.dumps(languages)
        pref.preferred_city = city_id if city_id else None
        
        db.session.add(pref)
        db.session.commit()
        
        flash('Preferences saved successfully!', 'success')
        return redirect(url_for('entertainment.entertainment_home'))
    
    # Get current preferences
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    current_prefs = {
        'genres': json.loads(pref.preferred_genres) if pref and pref.preferred_genres else [],
        'languages': json.loads(pref.preferred_languages) if pref and pref.preferred_languages else []
    }
    
    cities = City.query.filter_by(is_active=True).all()
    all_genres = ['Action', 'Comedy', 'Drama', 'Romance', 'Thriller', 'Horror', 'Sci-Fi']
    all_languages = ['Hindi', 'English', 'Marathi', 'Tamil', 'Telugu', 'Bengali', 'Punjabi']
    
    return render_template('user_preferences.html',
                         cities=cities,
                         all_genres=all_genres,
                         all_languages=all_languages,
                         current_prefs=current_prefs)

# API Routes for Seat Selection
@entertainment_bp.route('/api/seats/<int:show_id>')
def api_get_seats(show_id):
    """API to get seat layout"""
    seats = get_available_seats(show_id)
    return jsonify(seats)

@entertainment_bp.route('/api/price/<int:show_id>')
def api_calculate_price(show_id):
    """API to calculate dynamic price"""
    show = Show.query.get_or_404(show_id)
    selected_seats = request.args.getlist('seats')
    
    seats_data = get_available_seats(show_id)
    total = 0
    for seat in selected_seats:
        if seat in seats_data:
            multiplier = seats_data[seat]['price_multiplier']
            total += show.ticket_price * multiplier
    
    dynamic_price = calculate_dynamic_price(
        total / len(selected_seats) if selected_seats else show.ticket_price,
        show.show_time,
        show.show_date
    )
    
    return jsonify({
        'total': total,
        'dynamic_total': dynamic_price * len(selected_seats),
        'per_ticket': dynamic_price
    })
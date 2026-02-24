from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='en')
    
    # Relationships
    payments = db.relationship('Payment', backref='user', lazy=True)
    sips = db.relationship('SIP', backref='user', lazy=True)
    golds = db.relationship('Gold', backref='user', lazy=True)
    silvers = db.relationship('Silver', backref='user', lazy=True)
    recharges = db.relationship('Recharge', backref='user', lazy=True)
    bills = db.relationship('Bill', backref='user', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    upi_id = db.Column(db.String(100))
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    receipt_path = db.Column(db.String(200))
    qr_uploaded = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # SIP Model
class SIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fund_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20))  # monthly, quarterly
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    next_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    total_invested = db.Column(db.Float, default=0)
    current_value = db.Column(db.Float, default=0)
    returns = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Gold Model
class Gold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grams = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20))  # buy, sell
    status = db.Column(db.String(20), default='completed')
    certificate_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Silver Model
class Silver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grams = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20))  # buy, sell
    status = db.Column(db.String(20), default='completed')
    certificate_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Recharge Model
class Recharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    operator = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20))  # prepaid, postpaid
    plan = db.Column(db.String(100))
    status = db.Column(db.String(20), default='completed')
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Bill Model (Unified for all bills)
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bill_type = db.Column(db.String(50))  # electricity, water, gas, internet, property, credit_card, loan
    consumer_number = db.Column(db.String(100))
    operator = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='completed')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Loan Model
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_type = db.Column(db.String(50))  # home, car, personal, education, business
    lender = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    emi_amount = db.Column(db.Float)
    total_paid = db.Column(db.Float, default=0)
    remaining = db.Column(db.Float)
    next_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # FASTag Models
class FASTag(db.Model):
    __tablename__ = 'fastag'  # ← यह LINE जोड़ो
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_id = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(20))  # Car, Bike, Truck, Bus
    bank_name = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='fastags')
    transactions = db.relationship('FASTagTransaction', backref='fastag', lazy=True)

class FASTagTransaction(db.Model):
    __tablename__ = 'fas_tag_transaction'  # ← यह LINE जोड़ो
    id = db.Column(db.Integer, primary_key=True)
    fastag_id = db.Column(db.Integer, db.ForeignKey('fastag.id'), nullable=False)
    transaction_id = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20))  # recharge, toll_deduction
    toll_name = db.Column(db.String(200))
    location = db.Column(db.String(200))
    balance_before = db.Column(db.Float)
    balance_after = db.Column(db.Float)
    status = db.Column(db.String(20), default='completed')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FASTagRecharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fastag_id = db.Column(db.Integer, db.ForeignKey('fastag.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # UPI, Card, NetBanking
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    receipt_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='fastag_recharges')

    # Loan Payment Model
class LoanPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')
    # Entertainment Models - BookMyShow Like System
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    total_screens = db.Column(db.Integer, default=1)
    amenities = db.Column(db.Text)  # JSON: parking, food court, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('City', backref='theatres')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(50))  # Hindi, English, Marathi, etc.
    genre = db.Column(db.String(100))  # Action, Comedy, Drama
    duration = db.Column(db.Integer)  # in minutes
    release_date = db.Column(db.DateTime)
    poster_url = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    cast = db.Column(db.Text)  # JSON array
    crew = db.Column(db.Text)  # JSON array
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=False)
    screen_number = db.Column(db.Integer)
    show_date = db.Column(db.DateTime, nullable=False)
    show_time = db.Column(db.String(20))  # 10:30 AM, 2:00 PM, etc.
    ticket_price = db.Column(db.Float, nullable=False)
    dynamic_price = db.Column(db.Float)  # Peak pricing
    total_seats = db.Column(db.Integer, default=120)
    available_seats = db.Column(db.Integer, default=120)
    seat_layout = db.Column(db.Text)  # JSON for seat map
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    movie = db.relationship('Movie', backref='shows')
    theatre = db.relationship('Theatre', backref='shows')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # Concert, Comedy, Workshop
    venue = db.Column(db.String(200))
    address = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    event_time = db.Column(db.String(20))
    duration = db.Column(db.Integer)  # in minutes
    artist = db.Column(db.String(200))
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    ticket_price = db.Column(db.Float)
    total_tickets = db.Column(db.Integer)
    available_tickets = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('City', backref='events')

class SportsMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    sport_type = db.Column(db.String(50))  # Cricket, Football, Kabaddi
    team1 = db.Column(db.String(100))
    team2 = db.Column(db.String(100))
    venue = db.Column(db.String(200))
    match_date = db.Column(db.DateTime, nullable=False)
    match_time = db.Column(db.String(20))
    ticket_price_range = db.Column(db.String(100))  # "500-2000"
    total_tickets = db.Column(db.Integer)
    available_tickets = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('City', backref='sports')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_type = db.Column(db.String(20))  # movie, event, sports
    item_id = db.Column(db.Integer)  # show_id, event_id, match_id
    seats = db.Column(db.Text)  # JSON: ["A1", "A2", "B3"]
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    qr_code = db.Column(db.String(500))  # path to QR image
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='bookings')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(20))  # movie, event, sports
    item_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)  # 1-5
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='ratings')

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preferred_genres = db.Column(db.Text)  # JSON: ["Action", "Comedy"]
    preferred_languages = db.Column(db.Text)  # JSON: ["Hindi", "English"]
    preferred_city = db.Column(db.Integer, db.ForeignKey('city.id'))
    notification_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='preferences')
    # ============================================
    # REWARDS & CASHBACK SYSTEM
    # ============================================

class Wallet(db.Model):
    """User Wallet for balance and rewards"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)  # Main balance (₹)
    reward_points = db.Column(db.Integer, default=0)  # Reward points (100 points = ₹1)
    lifetime_earnings = db.Column(db.Float, default=0.0)
    lifetime_cashback = db.Column(db.Float, default=0.0)
    tier = db.Column(db.String(20), default='Bronze')  # Bronze, Silver, Gold, Platinum
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='wallet')

class Transaction(db.Model):
    """All financial transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    transaction_type = db.Column(db.String(50))  # credit, debit, cashback, reward
    amount = db.Column(db.Float, nullable=False)
    reward_points = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))
    reference_id = db.Column(db.String(100))  # Bill ID, Recharge ID, etc.
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='transactions')
    wallet = db.relationship('Wallet', backref='transactions')

class Cashback(db.Model):
    """Cashback on specific transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    amount = db.Column(db.Float, nullable=False)  # Cashback amount
    percentage = db.Column(db.Float)  # Cashback percentage
    category = db.Column(db.String(50))  # bill, recharge, entertainment, fastag
    description = db.Column(db.String(200))
    credited_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='cashbacks')

class Reward(db.Model):
    """Reward points earned"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100))  # signup, referral, daily_checkin, achievement
    reference_id = db.Column(db.String(100))
    expires_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='rewards')

class Referral(db.Model):
    """Referral program"""
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who referred
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)  # Who joined
    referral_code = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, expired
    reward_amount = db.Column(db.Float, default=0.0)
    reward_points = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_sent')
    referred = db.relationship('User', foreign_keys=[referred_id], backref='referred_by')

class DailyReward(db.Model):
    """Daily check-in rewards"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.Integer)  # Day 1, Day 2, Day 3, etc.
    reward_type = db.Column(db.String(20))  # points, cashback, coupon
    reward_value = db.Column(db.Float)
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='daily_rewards')

class Achievement(db.Model):
    """User achievements and badges"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_name = db.Column(db.String(100))
    badge_icon = db.Column(db.String(50))
    description = db.Column(db.String(200))
    points_earned = db.Column(db.Integer, default=0)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='achievements')

class Offer(db.Model):
    """Special offers and promotions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    offer_type = db.Column(db.String(50))  # cashback, discount, points_multiplier
    discount_percentage = db.Column(db.Float)
    max_discount = db.Column(db.Float)
    min_transaction = db.Column(db.Float)
    applicable_on = db.Column(db.String(100))  # all, bills, recharge, entertainment
    coupon_code = db.Column(db.String(50), unique=True)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    usage_limit = db.Column(db.Integer)
    times_used = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Coupon(db.Model):
    """User coupons"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'))
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='active')  # active, used, expired
    used_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='coupons')
    offer = db.relationship('Offer', backref='coupons')
    # ============================================
    # TRAVEL BOOKING SYSTEM
    # ============================================

class TravelCity(db.Model):
    """Cities for travel"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='India')
    airport_code = db.Column(db.String(10))  # BOM, DEL, etc.
    railway_code = db.Column(db.String(10))  # CSTM, NDLS, etc.
    is_metro = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Airline(db.Model):
    """Airlines information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    iata_code = db.Column(db.String(10), unique=True)  # 6E, AI, etc.
    logo_url = db.Column(db.String(500))
    is_international = db.Column(db.Boolean, default=False)
    baggage_allowance = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Flight(db.Model):
    """Flight schedules"""
    id = db.Column(db.Integer, primary_key=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)
    flight_number = db.Column(db.String(20), unique=True)
    from_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    to_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in minutes
    price_economy = db.Column(db.Float)
    price_business = db.Column(db.Float)
    seats_economy = db.Column(db.Integer)
    seats_business = db.Column(db.Integer)
    available_economy = db.Column(db.Integer)
    available_business = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    airline = db.relationship('Airline', backref='flights')
    from_city = db.relationship('TravelCity', foreign_keys=[from_city_id])
    to_city = db.relationship('TravelCity', foreign_keys=[to_city_id])

class Train(db.Model):
    """Train schedules"""
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(20), unique=True)
    train_name = db.Column(db.String(100))
    from_station = db.Column(db.String(50))
    to_station = db.Column(db.String(50))
    from_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'))
    to_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'))
    departure_time = db.Column(db.String(20))
    arrival_time = db.Column(db.String(20))
    duration = db.Column(db.String(20))
    classes = db.Column(db.Text)  # JSON: {"SL": 500, "3A": 1200, "2A": 1800, "1A": 3000}
    available_seats = db.Column(db.Text)  # JSON: {"SL": 100, "3A": 80, "2A": 40, "1A": 20}
    running_days = db.Column(db.String(50))  # "Mon,Tue,Wed"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BusOperator(db.Model):
    """Bus operators"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(500))
    types = db.Column(db.String(200))  # AC, Non-AC, Sleeper, Seater
    rating = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bus(db.Model):
    """Bus schedules"""
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('bus_operator.id'), nullable=False)
    bus_number = db.Column(db.String(50))
    from_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    to_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    bus_type = db.Column(db.String(50))  # AC Sleeper, Non-AC Seater, etc.
    departure_time = db.Column(db.String(20))
    arrival_time = db.Column(db.String(20))
    duration = db.Column(db.String(20))
    price = db.Column(db.Float)
    total_seats = db.Column(db.Integer)
    available_seats = db.Column(db.Integer)
    boarding_points = db.Column(db.Text)  # JSON array
    dropping_points = db.Column(db.Text)  # JSON array
    amenities = db.Column(db.Text)  # JSON array
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    operator = db.relationship('BusOperator', backref='buses')
    from_city = db.relationship('TravelCity', foreign_keys=[from_city_id])
    to_city = db.relationship('TravelCity', foreign_keys=[to_city_id])

class Hotel(db.Model):
    """Hotels information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    address = db.Column(db.Text)
    star_rating = db.Column(db.Integer)  # 1-5
    description = db.Column(db.Text)
    amenities = db.Column(db.Text)  # JSON array
    images = db.Column(db.Text)  # JSON array
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    checkin_time = db.Column(db.String(20))
    checkout_time = db.Column(db.String(20))
    policies = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('TravelCity', backref='hotels')

class HotelRoom(db.Model):
    """Hotel room types"""
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_type = db.Column(db.String(100))  # Deluxe, Suite, Presidential
    max_occupancy = db.Column(db.Integer)
    bed_type = db.Column(db.String(50))
    price_per_night = db.Column(db.Float)
    discount_price = db.Column(db.Float)
    total_rooms = db.Column(db.Integer)
    available_rooms = db.Column(db.Integer)
    amenities = db.Column(db.Text)  # JSON array
    images = db.Column(db.Text)  # JSON array
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hotel = db.relationship('Hotel', backref='rooms')

class Cab(db.Model):
    """Cab services"""
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(100))  # Uber, Ola, Meru
    cab_type = db.Column(db.String(50))  # Micro, Mini, Sedan, SUV
    city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    base_fare = db.Column(db.Float)
    per_km = db.Column(db.Float)
    per_minute = db.Column(db.Float)
    min_fare = db.Column(db.Float)
    night_charge = db.Column(db.Float)
    capacity = db.Column(db.Integer)
    luggage_capacity = db.Column(db.Integer)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('TravelCity', backref='cabs')

class HolidayPackage(db.Model):
    """Holiday packages"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    destination_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'), nullable=False)
    duration = db.Column(db.Integer)  # in days
    nights = db.Column(db.Integer)
    days = db.Column(db.Integer)
    itinerary = db.Column(db.Text)  # JSON array
    inclusions = db.Column(db.Text)  # JSON array
    exclusions = db.Column(db.Text)  # JSON array
    price_per_person = db.Column(db.Float)
    discount_price = db.Column(db.Float)
    hotel_category = db.Column(db.String(50))  # 3*, 4*, 5*
    meal_plan = db.Column(db.String(50))  # EP, CP, MAP, AP
    images = db.Column(db.Text)  # JSON array
    start_dates = db.Column(db.Text)  # JSON array
    max_participants = db.Column(db.Integer)
    available_slots = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    destination = db.relationship('TravelCity', backref='packages')

class TravelBooking(db.Model):
    """All travel bookings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_type = db.Column(db.String(20))  # flight, train, bus, hotel, cab, package
    reference_id = db.Column(db.String(100))  # Flight ID, Hotel ID, etc.
    booking_details = db.Column(db.Text)  # JSON with all details
    pnr_number = db.Column(db.String(50), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, completed
    cancellation_reason = db.Column(db.Text)
    refund_amount = db.Column(db.Float, default=0.0)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    travel_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='travel_bookings')

class TravelPassenger(db.Model):
    """Passenger details for bookings"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('travel_booking.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    id_proof_type = db.Column(db.String(50))  # Aadhar, Passport, DL
    id_proof_number = db.Column(db.String(50))
    seat_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    booking = db.relationship('TravelBooking', backref='passengers')

class TravelInsurance(db.Model):
    """Travel insurance policies"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('travel_booking.id'), nullable=False)
    provider = db.Column(db.String(100))
    policy_number = db.Column(db.String(50), unique=True)
    coverage_amount = db.Column(db.Float)
    premium_amount = db.Column(db.Float)
    coverage_type = db.Column(db.String(100))  # Medical, Baggage, Cancellation
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    booking = db.relationship('TravelBooking', backref='insurance')

class PriceAlert(db.Model):
    """Price alerts for users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    alert_type = db.Column(db.String(20))  # flight, train, bus, hotel
    from_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'))
    to_city_id = db.Column(db.Integer, db.ForeignKey('travel_city.id'))
    travel_date = db.Column(db.DateTime)
    target_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    is_triggered = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='price_alerts')

class TravelReview(db.Model):
    """Reviews for hotels, flights, etc."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(20))  # hotel, flight, train, bus, package
    item_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)  # 1-5
    review = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON array
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='travel_reviews')
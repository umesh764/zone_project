from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from modules.models import db, LocalShop
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app

market_bp = Blueprint('market', __name__, url_prefix='/market')

# Categories predefined
CATEGORIES = [
    '👕 Garment', '👗 Women Fashion', '👔 Men Wear',
    '💇 Salon', '🍕 Restaurant', '📱 Electronics',
    '🛒 Grocery', '🎁 Gift Shop', '🏪 General Store',
    '💊 Medical', '📚 Stationery', '🔧 Services'
]

@market_bp.route('/')
def home():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    shops = LocalShop.query.filter_by(is_active=True)
    
    if query:
        shops = shops.filter(
            db.or_(
                LocalShop.shop_name.ilike(f'%{query}%'),
                LocalShop.items.ilike(f'%{query}%'),
                LocalShop.description.ilike(f'%{query}%')
            )
        )
    
    if category:
        shops = shops.filter_by(category=category)
    
    shops = shops.order_by(LocalShop.created_at.desc()).all()
    
    return render_template('market/home.html',
                         shops=shops,
                         categories=CATEGORIES,
                         selected_category=category,
                         search_query=query)

@market_bp.route('/shop/<int:shop_id>')
def shop_detail(shop_id):
    shop = LocalShop.query.get_or_404(shop_id)
    return render_template('market/shop_detail.html', shop=shop)

@market_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_shop():
    if request.method == 'POST':
        # Handle image upload
        image_url = None
        if 'shop_image' in request.files:
            file = request.files['shop_image']
            if file and file.filename != '':
                # Secure filename
                filename = secure_filename(file.filename)
                # Add timestamp to avoid duplicate
                import time
                filename = str(int(time.time())) + '_' + filename
                # Save file
                upload_path = os.path.join('static/uploads', filename)
                file.save(os.path.join(current_app.root_path, upload_path))
                image_url = url_for('static', filename=f'uploads/{filename}')
        
        shop = LocalShop(
            shop_name=request.form.get('shop_name'),
            owner_name=request.form.get('owner_name'),
            category=request.form.get('category'),
            address=request.form.get('address'),
            area=request.form.get('area'),
            phone=request.form.get('phone'),
            whatsapp=request.form.get('whatsapp'),
            items=request.form.get('items'),
            description=request.form.get('description'),
            opening_time=request.form.get('opening_time'),
            closing_time=request.form.get('closing_time'),
            is_open_sunday=request.form.get('is_open_sunday') == 'true',
            image_url=image_url,  # ✅ Save image URL
            added_by=current_user.id
        )
        
        db.session.add(shop)
        db.session.commit()
        
        flash('✅ Shop added successfully!', 'success')
        return redirect(url_for('market.home'))
    
    return render_template('market/add_shop.html', categories=CATEGORIES)

@market_bp.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    shops = LocalShop.query.filter(
        db.or_(
            LocalShop.shop_name.ilike(f'%{query}%'),
            LocalShop.items.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.shop_name,
        'category': s.category,
        'whatsapp': s.get_whatsapp_link()
    } for s in shops])

@market_bp.route('/order/<int:shop_id>')
def order_via_whatsapp(shop_id):
    shop = LocalShop.query.get_or_404(shop_id)
    item = request.args.get('item', '')
    return redirect(shop.get_whatsapp_link(f"I want to order: {item}"))
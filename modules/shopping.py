from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from modules.models import db, Payment
import uuid
from datetime import datetime

shopping_bp = Blueprint('shopping', __name__)

# Main Shopping Hub
@shopping_bp.route('/shopping')
def shopping_home():
    return render_template('shopping_home.html')

# ============================================
# E-COMMERCE PLATFORMS
# ============================================

@shopping_bp.route('/shopping/ajio')
def ajio():
    """Ajio - Lifestyle"""
    return render_template('ajio.html')

@shopping_bp.route('/shopping/meesho')
def meesho():
    """Meesho - Social Commerce"""
    return render_template('meesho.html')

@shopping_bp.route('/shopping/snapdeal')
def snapdeal():
    """Snapdeal"""
    return render_template('snapdeal.html')


# ============================================
# QUICK COMMERCE - 10 MIN DELIVERY
# ============================================

@shopping_bp.route('/shopping/blinkit')
def blinkit():
    """Blinkit - 10 min delivery"""
    return render_template('blinkit.html')

@shopping_bp.route('/shopping/zepto')
def zepto():
    """Zepto - 10 min delivery"""
    return render_template('zepto.html')
@shopping_bp.route('/shopping/spencers')
def spencers():
    return render_template('spencers.html')

@shopping_bp.route('/shopping/instamart')
def instamart():
    """Swiggy Instamart"""
    return render_template('instamart.html')

@shopping_bp.route('/shopping/bigbasket')
def bigbasket():
    """BigBasket - Grocery"""
    return render_template('bigbasket.html')
@shopping_bp.route('/shopping/relianceretail')
def relianceretail():
    return render_template('relianceretail.html')
@shopping_bp.route('/shopping/naturesbasket')
def naturesbasket():
    return render_template('naturesbasket.html')

@shopping_bp.route('/shopping/jiomart')
def jiomart():
    """JioMart - Reliance"""
    return render_template('jiomart.html')

# ============================================
# FOOD DELIVERY
# ============================================

@shopping_bp.route('/shopping/swiggy')
def swiggy():
    """Swiggy - Food Delivery"""
    return render_template('swiggy.html')

@shopping_bp.route('/shopping/zomato')
def zomato():
    """Zomato - Food Delivery"""
    return render_template('zomato.html')

@shopping_bp.route('/shopping/eatsure')
def eatsure():
    """EatSure - Rebel Foods"""
    return render_template('eatsure.html')

# ============================================
# BEAUTY & PERSONAL CARE
# ============================================

@shopping_bp.route('/shopping/nykaa')
def nykaa():
    """Nykaa - Beauty"""
    return render_template('nykaa.html')

@shopping_bp.route('/shopping/purplle')
def purplle():
    """Purplle - Beauty"""
    return render_template('purplle.html')

# ============================================
# ELECTRONICS & GADGETS
# ============================================

@shopping_bp.route('/shopping/croma')
def croma():
    """Croma - Electronics"""
    return render_template('croma.html')

@shopping_bp.route('/shhopping/reliancedigital')
def reliance_digital():
    """Reliance Digital"""
    return render_template('reliance_digital.html')
# ============================================
# ENTERTAINMENT
# ============================================

@shopping_bp.route('/entertainment/bookmyshow')
def bookmyshow():
    return render_template('bookmyshow.html')

@shopping_bp.route('/entertainment/pvrcinemas')
def pvrcinemas():
    return render_template('pvrcinemas.html')

@shopping_bp.route('/entertainment/inox')
def inox():
    return render_template('inox.html')

# ============================================
# OTHER SERVICES
# ============================================

@shopping_bp.route('/shopping/urbancompany')
def urbancompany():
    return render_template('urbancompany.html')

@shopping_bp.route('/shopping/practo')
def practo():
    return render_template('practo.html')

@shopping_bp.route('/shopping/curefit')
def curefit():
    return render_template('curefit.html')

# ============================================
# PHARMACY
# ============================================

@shopping_bp.route('/shopping/pharmeasy')
def pharmeasy():
    """PharmEasy - Medicine"""
    return render_template('pharmeasy.html')
@shopping_bp.route('/shopping/dunzo')
def dunzo():
    return render_template('dunzo.html')

@shopping_bp.route('/shhopping/bbnow')
def bbnow():
    return render_template('bbnow.html')

@shopping_bp.route('/shopping/1mg')
def one_mg():
    """1mg - Healthcare"""
    return render_template('1mg.html')

@shopping_bp.route('/shopping/netmeds')
def netmeds():
    """NetMeds - Pharmacy"""
    return render_template('netmeds.html')

# ============================================
# BACKWARD COMPATIBILITY (पुराने links भी काम करेंगे)
# ============================================

@shopping_bp.route('/shopping/amazon-deals')
def amazon_deals():
    return redirect(url_for('shopping.amazon'))

@shopping_bp.route('/shopping/flipkart-offers')
def flipkart_offers():
    return redirect(url_for('shopping.flipkart'))
@shopping_bp.route('/shopping/flipkart')
def flipkart():
    return render_template('flipkart.html')

@shopping_bp.route('/shopping/food')
def food_deals():
    return redirect(url_for('shopping.swiggy'))
# ============================================
# DIRECT BUY FUNCTIONALITY
# ============================================

@shopping_bp.route('/shopping/buy/<platform>/<product_id>')
@login_required
def buy_product(platform, product_id):
    """Direct buy product"""
    # Mock product data (in real app, fetch from API)
    products = {
        'amazon': {
            'B01N5Q8JKL': {'name': 'iPhone 15', 'price': 79999, 'image': 'iphone.jpg'},
            'B08L5VKJHG': {'name': 'Samsung TV', 'price': 45999, 'image': 'tv.jpg'},
        },
        'flipkart': {
            'MOB12345': {'name': 'OnePlus 12', 'price': 64999, 'image': 'oneplus.jpg'},
            'TEL98765': {'name': 'Mi TV', 'price': 29999, 'image': 'mitv.jpg'},
        }
    }
    
    product = products.get(platform, {}).get(product_id, None)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('shopping.shopping_home'))
    
    return render_template('buy_product.html', 
                         platform=platform,
                         product=product,
                         product_id=product_id)

@shopping_bp.route('/shopping/checkout', methods=['POST'])
@login_required
def checkout():
    """Process checkout and payment"""
    platform = request.form.get('platform')
    product_id = request.form.get('product_id')
    product_name = request.form.get('product_name')
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity', 1))
    total = price * quantity
    
    # Create transaction
    transaction_id = f"ORD{uuid.uuid4().hex[:12].upper()}"
    
    # Save to database
    payment = Payment(
        user_id=current_user.id,
        amount=total,
        transaction_id=transaction_id,
        status='completed',
        payment_method='shopping',
        description=f"Bought {product_name} from {platform}"
    )
    db.session.add(payment)
    db.session.commit()
    
    # Generate receipt
    receipt_data = {
        'transaction_id': transaction_id,
        'platform': platform,
        'product': product_name,
        'quantity': quantity,
        'price': price,
        'total': total,
        'date': datetime.utcnow().strftime('%d-%m-%Y %H:%M')
    }
    
    flash(f'Order placed successfully! Order ID: {transaction_id}', 'success')
    return render_template('order_confirmation.html', receipt=receipt_data)

@shopping_bp.route('/shopping/quick-buy/<platform>')
def quick_buy(platform):
    """Quick buy page for a platform"""
    return render_template(f'{platform}_products.html')
# ============================================
# ALL SHOPPING SITES
# ============================================

# E-Commerce
@shopping_bp.route('/shopping/amazon')
def amazon():
    return render_template('amazon.html')


@shopping_bp.route('/shopping/dmart')
def dmart():
    return render_template('dmart.html')

@shopping_bp.route('/shopping/faasos')
def faasos():
    return render_template('faasos.html')

@shopping_bp.route('/shopping/quick-commerce')
def quick_commerce():
    """All quick commerce apps"""
    return render_template('quick_commerce.html')
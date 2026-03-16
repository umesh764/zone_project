from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from modules.models import db, Payment
import uuid
from datetime import datetime

shopping_bp = Blueprint('shopping', __name__, url_prefix='/shopping')

# ============================================
# SHOPPING HOME
# ============================================
@shopping_bp.route('/')
def shopping_home():
    return render_template('shopping_home.html')


# ============================================
# E-COMMERCE PLATFORMS - DIRECT REDIRECT
# ============================================
@shopping_bp.route('/amazon')
def amazon():
    return redirect('https://www.amazon.in')

@shopping_bp.route('/flipkart')
def flipkart():
    return redirect('https://www.flipkart.com')

@shopping_bp.route('/myntra')
def myntra():
    return redirect('https://www.myntra.com')

@shopping_bp.route('/ajio')
def ajio():
    return redirect('https://www.ajio.com')

@shopping_bp.route('/meesho')
def meesho():
    return redirect('https://www.meesho.com')

@shopping_bp.route('/snapdeal')
def snapdeal():
    return redirect('https://www.snapdeal.com')


# ============================================
# DEALS & OFFERS
# ============================================
@shopping_bp.route('/amazon-deals')
def amazon_deals():
    return redirect('https://www.amazon.in/deals')

@shopping_bp.route('/flipkart-offers')
def flipkart_offers():
    return redirect('https://www.flipkart.com/offers')

@shopping_bp.route('/deals')
def deals():
    return redirect('https://www.amazon.in/deals')


# ============================================
# FOOD DELIVERY
# ============================================
@shopping_bp.route('/food')
def food_deals():
    return redirect('https://www.swiggy.com')

@shopping_bp.route('/swiggy')
def swiggy():
    return redirect('https://www.swiggy.com')

@shopping_bp.route('/zomato')
def zomato():
    return redirect('https://www.zomato.com')

@shopping_bp.route('/eatsure')
def eatsure():
    return redirect('https://www.eatsure.com')


# ============================================
# QUICK COMMERCE
# ============================================
@shopping_bp.route('/quick-commerce')
def quick_commerce():
    return render_template('quick_commerce.html')  # यहाँ सबकी लिस्ट दिखाएँ

@shopping_bp.route('/blinkit')
def blinkit():
    return redirect('https://blinkit.com')

@shopping_bp.route('/zepto')
def zepto():
    return redirect('https://www.zepto.com')

@shopping_bp.route('/instamart')
def instamart():
    return redirect('https://www.swiggy.com/instamart')

@shopping_bp.route('/bigbasket')
def bigbasket():
    return redirect('https://www.bigbasket.com')

@shopping_bp.route('/dmart')
def dmart():
    return redirect('https://www.dmart.in')


# ============================================
# BEAUTY & HEALTH
# ============================================
@shopping_bp.route('/nykaa')
def nykaa():
    return redirect('https://www.nykaa.com')

@shopping_bp.route('/purplle')
def purplle():
    return redirect('https://www.purplle.com')

# ============================================
# FASHION HUB
# ============================================
@shopping_bp.route('/fashion')
def fashion():
    return redirect('https://www.myntra.com')


# ============================================
# GROCERY
# ============================================
@shopping_bp.route('/spencers')
def spencers():
    return redirect('https://www.spencers.in')

@shopping_bp.route('/relianceretail')
def relianceretail():
    return redirect('https://www.relianceretail.com')

@shopping_bp.route('/naturesbasket')
def naturesbasket():
    return redirect('https://www.naturesbasket.co.in')

@shopping_bp.route('/jiomart')
def jiomart():
    return redirect('https://www.jiomart.com')


# ============================================
# ELECTRONICS
# ============================================
@shopping_bp.route('/croma')
def croma():
    return redirect('https://www.croma.com')

@shopping_bp.route('/reliancedigital')
def reliance_digital():
    return redirect('https://www.reliancedigital.in')


# ============================================
# OTHER SERVICES
# ============================================
@shopping_bp.route('/urbancompany')
def urbancompany():
    return redirect('https://www.urbancompany.com')

@shopping_bp.route('/practo')
def practo():
    return redirect('https://www.practo.com')

@shopping_bp.route('/curefit')
def curefit():
    return redirect('https://www.curefit.com')

@shopping_bp.route('/dunzo')
def dunzo():
    return redirect('https://www.dunzo.com')


# ============================================
# ENTERTAINMENT
# ============================================
@shopping_bp.route('/bookmyshow')
def bookmyshow():
    return redirect('https://in.bookmyshow.com')

@shopping_bp.route('/pvrcinemas')
def pvrcinemas():
    return redirect('https://www.pvrcinemas.com')

@shopping_bp.route('/inox')
def inox():
    return redirect('https://www.inoxmovies.com')


# ============================================
# PHARMACY
# ============================================
@shopping_bp.route('/pharmeasy')
def pharmeasy():
    return redirect('https://pharmeasy.in')

@shopping_bp.route('/1mg')
def one_mg():
    return redirect('https://www.1mg.com')

@shopping_bp.route('/netmeds')
def netmeds():
    return redirect('https://www.netmeds.com')


# ============================================
# DIRECT BUY FUNCTIONALITY (यदि चाहिए तो)
# ============================================
@shopping_bp.route('/buy/<platform>/<product_id>')
@login_required
def buy_product(platform, product_id):
    """Direct buy product - internal page"""
    return render_template('buy_product.html', platform=platform, product_id=product_id)


@shopping_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Process checkout and payment"""
    return redirect(url_for('shopping.shopping_home'))


@shopping_bp.route('/quick-buy/<platform>')
def quick_buy(platform):
    """Quick buy page for a platform"""
    return redirect(f'https://www.{platform}.com')
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from modules.models import db, Wallet, Transaction, Cashback, Reward, Referral, DailyReward, Achievement, Offer, Coupon, User
import uuid
import random
import string
from datetime import datetime, timedelta
import json

rewards_bp = Blueprint('rewards', __name__)

# ============================================
# CASHBACK CALCULATION ALGORITHM
# ============================================

def calculate_cashback(amount, category, user_tier='Bronze'):
    """AI-based cashback calculation"""
    base_percentage = {
        'Bronze': 0.5,   # 0.5%
        'Silver': 1.0,   # 1%
        'Gold': 1.5,     # 1.5%
        'Platinum': 2.0  # 2%
    }
    
    # Category multipliers
    category_multiplier = {
        'bill': 1.0,
        'recharge': 1.2,
        'entertainment': 1.5,
        'fastag': 1.0,
        'shopping': 2.0,
        'investment': 2.5
    }
    
    # Calculate cashback
    percentage = base_percentage.get(user_tier, 0.5) * category_multiplier.get(category, 1.0)
    cashback = (amount * percentage) / 100
    
    # Max cashback limit
    max_cashback = {
        'Bronze': 100,
        'Silver': 250,
        'Gold': 500,
        'Platinum': 1000
    }
    
    return min(cashback, max_cashback.get(user_tier, 100))

def calculate_reward_points(amount, transaction_type):
    """Calculate reward points based on transaction"""
    # 1 point per ₹10 spent
    points = int(amount / 10)
    
    # Bonus for certain transactions
    if transaction_type == 'entertainment':
        points += 5
    elif transaction_type == 'fastag':
        points += 3
    
    return points

# ============================================
# TIER UPGRADE ALGORITHM
# ============================================

def update_user_tier(user_id):
    """Update user tier based on lifetime earnings"""
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return
    
    lifetime = wallet.lifetime_earnings
    
    if lifetime >= 50000:
        new_tier = 'Platinum'
    elif lifetime >= 25000:
        new_tier = 'Gold'
    elif lifetime >= 10000:
        new_tier = 'Silver'
    else:
        new_tier = 'Bronze'
    
    if new_tier != wallet.tier:
        old_tier = wallet.tier
        wallet.tier = new_tier
        db.session.commit()
        
        # Award tier upgrade bonus
        add_reward_points(user_id, 100, f'Tier upgraded from {old_tier} to {new_tier}')
        
        # Create achievement
        achievement = Achievement(
            user_id=user_id,
            badge_name=f'{new_tier} Member',
            badge_icon=f'badge-{new_tier.lower()}.png',
            description=f'Congratulations! You are now a {new_tier} member',
            points_earned=100
        )
        db.session.add(achievement)
        db.session.commit()

# ============================================
# WALLET FUNCTIONS
# ============================================

def get_or_create_wallet(user_id):
    """Get user wallet or create if not exists"""
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(
            user_id=user_id,
            balance=0,
            reward_points=0,
            lifetime_earnings=0,
            lifetime_cashback=0,
            tier='Bronze'
        )
        db.session.add(wallet)
        db.session.commit()
    return wallet

def add_balance(user_id, amount, description, reference_id=None):
    """Add money to wallet"""
    wallet = get_or_create_wallet(user_id)
    wallet.balance += amount
    wallet.lifetime_earnings += amount
    
    transaction = Transaction(
        user_id=user_id,
        wallet_id=wallet.id,
        transaction_type='credit',
        amount=amount,
        description=description,
        reference_id=reference_id
    )
    db.session.add(transaction)
    db.session.commit()
    
    update_user_tier(user_id)
    return transaction

def deduct_balance(user_id, amount, description, reference_id=None):
    """Deduct money from wallet"""
    wallet = get_or_create_wallet(user_id)
    
    if wallet.balance < amount:
        return False
    
    wallet.balance -= amount
    
    transaction = Transaction(
        user_id=user_id,
        wallet_id=wallet.id,
        transaction_type='debit',
        amount=amount,
        description=description,
        reference_id=reference_id
    )
    db.session.add(transaction)
    db.session.commit()
    
    return transaction

def add_cashback(user_id, amount, category, transaction_id=None):
    """Add cashback to wallet"""
    wallet = get_or_create_wallet(user_id)
    cashback_amount = calculate_cashback(amount, category, wallet.tier)
    
    if cashback_amount > 0:
        wallet.balance += cashback_amount
        wallet.lifetime_cashback += cashback_amount
        
        cashback = Cashback(
            user_id=user_id,
            transaction_id=transaction_id,
            amount=cashback_amount,
            percentage=(cashback_amount/amount)*100,
            category=category,
            description=f'Cashback on {category}'
        )
        db.session.add(cashback)
        
        transaction = Transaction(
            user_id=user_id,
            wallet_id=wallet.id,
            transaction_type='cashback',
            amount=cashback_amount,
            description=f'Cashback on {category}',
            reference_id=transaction_id
        )
        db.session.add(transaction)
        db.session.commit()
        
        return cashback_amount
    
    return 0

def add_reward_points(user_id, points, reason, reference_id=None):
    """Add reward points to user"""
    wallet = get_or_create_wallet(user_id)
    wallet.reward_points += points
    
    reward = Reward(
        user_id=user_id,
        points=points,
        reason=reason,
        reference_id=reference_id,
        expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year validity
    )
    db.session.add(reward)
    db.session.commit()
    
    return reward

# ============================================
# REFERRAL FUNCTIONS
# ============================================

def generate_referral_code():
    """Generate unique referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Referral.query.filter_by(referral_code=code).first():
            return code

def process_referral(referrer_id, referred_id):
    """Process referral reward"""
    # Check if already referred
    existing = Referral.query.filter_by(referred_id=referred_id).first()
    if existing:
        return False
    
    # Create referral record
    referral = Referral(
        referrer_id=referrer_id,
        referred_id=referred_id,
        referral_code=generate_referral_code(),
        status='completed',
        joined_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        reward_amount=100,  # ₹100 reward
        reward_points=500   # 500 points
    )
    db.session.add(referral)
    
    # Add reward to referrer
    add_balance(referrer_id, 100, 'Referral bonus')
    add_reward_points(referrer_id, 500, 'Referral bonus')
    
    # Add welcome bonus to referred user
    add_balance(referred_id, 50, 'Welcome bonus')
    add_reward_points(referred_id, 200, 'Welcome bonus')
    
    db.session.commit()
    return True

# ============================================
# DAILY REWARDS
# ============================================

def get_daily_reward(user_id):
    """Get daily check-in reward"""
    today = datetime.utcnow().date()
    
    # Check if already claimed today
    claimed = DailyReward.query.filter(
        DailyReward.user_id == user_id,
        db.func.date(DailyReward.claimed_at) == today
    ).first()
    
    if claimed:
        return None
    
    # Get last claim to determine streak
    last_claim = DailyReward.query.filter_by(user_id=user_id)\
        .order_by(DailyReward.claimed_at.desc()).first()
    
    if last_claim and (datetime.utcnow().date() - last_claim.claimed_at.date()).days == 1:
        day = last_claim.day + 1
    else:
        day = 1
    
    # Calculate reward based on streak
    rewards = {
        1: {'points': 10, 'cashback': 1},
        2: {'points': 20, 'cashback': 2},
        3: {'points': 30, 'cashback': 3},
        4: {'points': 40, 'cashback': 4},
        5: {'points': 50, 'cashback': 5},
        6: {'points': 60, 'cashback': 6},
        7: {'points': 100, 'cashback': 10},
    }
    
    reward = rewards.get(day, {'points': 10, 'cashback': 1})
    
    # Award reward
    if reward['points'] > 0:
        add_reward_points(user_id, reward['points'], f'Daily check-in day {day}')
    
    if reward['cashback'] > 0:
        add_balance(user_id, reward['cashback'], f'Daily check-in bonus day {day}')
    
    # Record claim
    daily = DailyReward(
        user_id=user_id,
        day=day,
        reward_type='points_cashback',
        reward_value=reward['points']
    )
    db.session.add(daily)
    db.session.commit()
    
    return {'day': day, 'points': reward['points'], 'cashback': reward['cashback']}

# ============================================
# ACHIEVEMENTS
# ============================================

def check_achievements(user_id):
    """Check and award achievements"""
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return
    
    achievements = []
    
    # First transaction
    if Transaction.query.filter_by(user_id=user_id).count() == 1:
        if not Achievement.query.filter_by(user_id=user_id, badge_name='First Transaction').first():
            achievements.append({
                'name': 'First Transaction',
                'icon': '🎯',
                'desc': 'Made your first transaction',
                'points': 50
            })
    
    # First cashback
    if Cashback.query.filter_by(user_id=user_id).count() == 1:
        if not Achievement.query.filter_by(user_id=user_id, badge_name='Cashback Starter').first():
            achievements.append({
                'name': 'Cashback Starter',
                'icon': '💰',
                'desc': 'Earned your first cashback',
                'points': 50
            })
    
    # Milestone achievements
    milestones = {
        1000: '₹1000 Club',
        5000: '₹5000 Club',
        10000: '₹10,000 Club',
        25000: '₹25,000 Club',
        50000: '₹50,000 Club'
    }
    
    for amount, badge in milestones.items():
        if wallet.lifetime_earnings >= amount:
            if not Achievement.query.filter_by(user_id=user_id, badge_name=badge).first():
                achievements.append({
                    'name': badge,
                    'icon': '🏆',
                    'desc': f'Spent over {badge}',
                    'points': 100
                })
    
    # Referral achievement
    if Referral.query.filter_by(referrer_id=user_id).count() >= 5:
        if not Achievement.query.filter_by(user_id=user_id, badge_name='Super Referrer').first():
            achievements.append({
                'name': 'Super Referrer',
                'icon': '🤝',
                'desc': 'Referred 5 friends',
                'points': 200
            })
    
    # Award achievements
    for ach in achievements:
        achievement = Achievement(
            user_id=user_id,
            badge_name=ach['name'],
            badge_icon=ach['icon'],
            description=ach['desc'],
            points_earned=ach['points']
        )
        db.session.add(achievement)
        add_reward_points(user_id, ach['points'], f'Achievement: {ach["name"]}')
    
    db.session.commit()

# ============================================
# ROUTES
# ============================================

@rewards_bp.route('/rewards')
@login_required
def rewards_dashboard():
    """Rewards dashboard"""
    wallet = get_or_create_wallet(current_user.id)
    
    # Get recent transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get cashbacks
    cashbacks = Cashback.query.filter_by(user_id=current_user.id)\
        .order_by(Cashback.credited_at.desc()).limit(5).all()
    
    # Get achievements
    achievements = Achievement.query.filter_by(user_id=current_user.id)\
        .order_by(Achievement.earned_at.desc()).all()
    
    # Get active offers
    offers = Offer.query.filter_by(is_active=True)\
        .filter(Offer.valid_until > datetime.utcnow())\
        .all()
    
    # Get referral info
    referral = Referral.query.filter_by(referrer_id=current_user.id).first()
    if not referral:
        referral_code = generate_referral_code()
        referral = Referral(
            referrer_id=current_user.id,
            referral_code=referral_code,
            status='active'
        )
        db.session.add(referral)
        db.session.commit()
    
    # Daily reward
    daily_reward = get_daily_reward(current_user.id)
    
    # Check achievements
    check_achievements(current_user.id)
    
    return render_template('rewards_dashboard.html',
                         wallet=wallet,
                         transactions=transactions,
                         cashbacks=cashbacks,
                         achievements=achievements,
                         offers=offers,
                         referral=referral,
                         daily_reward=daily_reward)

@rewards_bp.route('/rewards/claim-daily', methods=['POST'])
@login_required
def claim_daily_reward():
    """Claim daily reward"""
    reward = get_daily_reward(current_user.id)
    if reward:
        flash(f'Daily reward claimed! Day {reward["day"]}: +{reward["points"]} points, +₹{reward["cashback"]} cashback', 'success')
    else:
        flash('Already claimed today! Come back tomorrow.', 'info')
    
    return redirect(url_for('rewards.rewards_dashboard'))

@rewards_bp.route('/rewards/refer')
@login_required
def referral_page():
    """Referral page"""
    referral = Referral.query.filter_by(referrer_id=current_user.id).first()
    if not referral:
        referral_code = generate_referral_code()
        referral = Referral(
            referrer_id=current_user.id,
            referral_code=referral_code,
            status='active'
        )
        db.session.add(referral)
        db.session.commit()
    
    # Get referred users
    referred_users = Referral.query.filter_by(referrer_id=current_user.id)\
        .filter(Referral.referred_id.isnot(None)).all()
    
    return render_template('referral.html', referral=referral, referred_users=referred_users)

@rewards_bp.route('/rewards/convert-points', methods=['POST'])
@login_required
def convert_points():
    """Convert reward points to money"""
    points = int(request.form.get('points', 0))
    
    if points < 100:
        flash('Minimum 100 points required', 'error')
        return redirect(url_for('rewards.rewards_dashboard'))
    
    wallet = get_or_create_wallet(current_user.id)
    
    if wallet.reward_points < points:
        flash('Insufficient points', 'error')
        return redirect(url_for('rewards.rewards_dashboard'))
    
    # 100 points = ₹1
    amount = points / 100
    
    wallet.reward_points -= points
    wallet.balance += amount
    
    transaction = Transaction(
        user_id=current_user.id,
        wallet_id=wallet.id,
        transaction_type='credit',
        amount=amount,
        description=f'Converted {points} reward points'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    flash(f'Successfully converted {points} points to ₹{amount}', 'success')
    return redirect(url_for('rewards.rewards_dashboard'))

@rewards_bp.route('/rewards/history')
@login_required
def rewards_history():
    """Full rewards history"""
    page = request.args.get('page', 1, type=int)
    
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=20)
    
    cashbacks = Cashback.query.filter_by(user_id=current_user.id)\
        .order_by(Cashback.credited_at.desc())\
        .paginate(page=page, per_page=20)
    
    return render_template('rewards_history.html',
                         transactions=transactions,
                         cashbacks=cashbacks)

@rewards_bp.route('/api/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    """Apply coupon code"""
    data = request.json
    code = data.get('code').upper()
    amount = float(data.get('amount', 0))
    category = data.get('category')
    
    # Find offer
    offer = Offer.query.filter_by(coupon_code=code, is_active=True)\
        .filter(Offer.valid_until > datetime.utcnow()).first()
    
    if not offer:
        return jsonify({'success': False, 'message': 'Invalid coupon code'})
    
    if offer.usage_limit and offer.times_used >= offer.usage_limit:
        return jsonify({'success': False, 'message': 'Coupon usage limit exceeded'})
    
    if amount < offer.min_transaction:
        return jsonify({'success': False, 'message': f'Minimum transaction amount ₹{offer.min_transaction}'})
    
    # Calculate discount
    discount = (amount * offer.discount_percentage) / 100
    if offer.max_discount:
        discount = min(discount, offer.max_discount)
    
    # Update usage count
    offer.times_used += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'discount': discount,
        'final_amount': amount - discount,
        'message': f'Coupon applied! You saved ₹{discount}'
    })

@rewards_bp.route('/rewards/offers')
@login_required
def all_offers():
    """View all offers"""
    offers = Offer.query.filter_by(is_active=True)\
        .filter(Offer.valid_until > datetime.utcnow())\
        .order_by(Offer.valid_until).all()
    
    return render_template('offers.html', offers=offers)

@rewards_bp.route('/api/process-payment-reward', methods=['POST'])
@login_required
def process_payment_reward():
    """Process rewards after payment (called by other modules)"""
    data = request.json
    amount = data.get('amount')
    category = data.get('category')
    transaction_id = data.get('transaction_id')
    
    # Add cashback
    cashback = add_cashback(current_user.id, amount, category, transaction_id)
    
    # Add reward points
    points = calculate_reward_points(amount, category)
    if points > 0:
        add_reward_points(current_user.id, points, f'Reward points for {category}')
    
    return jsonify({
        'success': True,
        'cashback': cashback,
        'points': points
    })
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from modules.models import db, FASTag, FASTagTransaction, FASTagRecharge
import uuid
import random
from datetime import datetime, timedelta

fastag_bp = Blueprint('fastag', __name__)

# Indian Toll Plaza Data
TOLL_PLAZAS = [
    {"name": "Mumbai-Pune Expressway Toll", "location": "Khalapur, Maharashtra", "amount": 265},
    {"name": "Delhi-Gurugram Toll", "location": "Gurugram, Haryana", "amount": 140},
    {"name": "Bengaluru-Hyderabad Highway", "location": "Karnataka", "amount": 320},
    {"name": "Ahmedabad-Vadodara Expressway", "location": "Gujarat", "amount": 235},
    {"name": "Chennai-Bengaluru Highway", "location": "Tamil Nadu", "amount": 290},
    {"name": "Kolkata-Durgapur Expressway", "location": "West Bengal", "amount": 195},
    {"name": "Jaipur-Delhi Highway", "location": "Rajasthan", "amount": 215},
    {"name": "Lucknow-Kanpur Expressway", "location": "Uttar Pradesh", "amount": 175},
    {"name": "Nagpur-Mumbai Highway", "location": "Nagpur, Maharashtra", "amount": 445},
    {"name": "Pune-Bengaluru Highway", "location": "Satara, Maharashtra", "amount": 355}
]

# Vehicle Types and Rates
VEHICLE_TYPES = {
    "Car/Jeep/Van": 1.0,
    "LCV (Light Commercial Vehicle)": 1.5,
    "Truck/Bus": 2.5,
    "3-Axle Vehicle": 3.0,
    "HCM/EME": 4.0
}

def generate_tag_id():
    """Generate unique FASTag ID"""
    return f"FT{random.randint(1000, 9999)}{uuid.uuid4().hex[:6].upper()}"

@fastag_bp.route('/fastag', methods=['GET'])
@login_required
def fastag_dashboard():
    """FASTag Main Dashboard"""
    # Get user's FASTags
    fastags = FASTag.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals
    total_balance = sum(f.balance for f in fastags)
    active_tags = sum(1 for f in fastags if f.status == 'active')
    
    # Get recent transactions
    recent_transactions = []
    for fastag in fastags:
        transactions = FASTagTransaction.query.filter_by(fastag_id=fastag.id)\
            .order_by(FASTagTransaction.transaction_date.desc()).limit(5).all()
        recent_transactions.extend(transactions)
    
    # Sort by date
    recent_transactions.sort(key=lambda x: x.transaction_date, reverse=True)
    
    return render_template('fastag_dashboard.html', 
                         fastags=fastags,
                         total_balance=total_balance,
                         active_tags=active_tags,
                         recent_transactions=recent_transactions[:10])

@fastag_bp.route('/fastag/apply', methods=['GET', 'POST'])
@login_required
def apply_fastag():
    """Apply for new FASTag"""
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number').upper()
        vehicle_type = request.form.get('vehicle_type')
        bank_name = request.form.get('bank_name')
        
        # Validate vehicle number format (Indian format)
        import re
        vehicle_pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$'
        if not re.match(vehicle_pattern, vehicle_number):
            flash('Invalid vehicle number format! (e.g., MH12AB1234)', 'error')
            return redirect(url_for('fastag.apply_fastag'))
        
        # Check if vehicle already registered
        existing = FASTag.query.filter_by(vehicle_number=vehicle_number).first()
        if existing:
            flash('This vehicle already has a FASTag!', 'error')
            return redirect(url_for('fastag.apply_fastag'))
        
        # Create new FASTag
        tag_id = generate_tag_id()
        expiry_date = datetime.utcnow() + timedelta(days=365*5)  # 5 years validity
        
        fastag = FASTag(
            user_id=current_user.id,
            tag_id=tag_id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            bank_name=bank_name,
            balance=0,
            status='inactive',  # Will be activated after first recharge
            expiry_date=expiry_date
        )
        
        db.session.add(fastag)
        db.session.commit()
        
        flash(f'FASTag applied successfully! Tag ID: {tag_id}', 'success')
        return redirect(url_for('fastag.fastag_details', tag_id=tag_id))
    
    return render_template('apply_fastag.html', vehicle_types=VEHICLE_TYPES.keys())

@fastag_bp.route('/fastag/details/<tag_id>')
@login_required
def fastag_details(tag_id):
    """View FASTag details"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    # Get transactions
    transactions = FASTagTransaction.query.filter_by(fastag_id=fastag.id)\
        .order_by(FASTagTransaction.transaction_date.desc()).all()
    
    return render_template('fastag_details.html', fastag=fastag, transactions=transactions)

@fastag_bp.route('/fastag/recharge/<tag_id>', methods=['GET', 'POST'])
@login_required
def recharge_fastag(tag_id):
    """Recharge FASTag"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method', 'UPI')
        
        # Generate transaction ID
        txn_id = f"FTX{uuid.uuid4().hex[:12].upper()}"
        
        # Create recharge record
        recharge = FASTagRecharge(
            user_id=current_user.id,
            fastag_id=fastag.id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=txn_id,
            status='completed'
        )
        
        # Update balance
        old_balance = fastag.balance
        fastag.balance += amount
        fastag.status = 'active'  # Activate on first recharge
        
        # Create transaction record
        transaction = FASTagTransaction(
            fastag_id=fastag.id,
            transaction_id=txn_id,
            amount=amount,
            type='recharge',
            balance_before=old_balance,
            balance_after=fastag.balance,
            status='completed'
        )
        
        db.session.add(recharge)
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'FASTag recharged with ₹{amount} successfully!', 'success')
        return redirect(url_for('fastag.fastag_details', tag_id=tag_id))
    
    return render_template('recharge_fastag.html', fastag=fastag)

@fastag_bp.route('/fastag/balance/<tag_id>')
@login_required
def check_balance(tag_id):
    """Check FASTag balance"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'tag_id': fastag.tag_id,
        'vehicle': fastag.vehicle_number,
        'balance': fastag.balance,
        'status': fastag.status
    })

@fastag_bp.route('/fastag/simulate-toll/<tag_id>', methods=['POST'])
@login_required
def simulate_toll(tag_id):
    """Simulate toll deduction (for demo)"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    # Random toll plaza
    toll = random.choice(TOLL_PLAZAS)
    
    # Calculate amount based on vehicle type
    multiplier = VEHICLE_TYPES.get(fastag.vehicle_type, 1.0)
    amount = toll['amount'] * multiplier
    
    if fastag.balance < amount:
        return jsonify({
            'success': False,
            'message': 'Insufficient balance!',
            'required': amount,
            'balance': fastag.balance
        })
    
    # Process deduction
    old_balance = fastag.balance
    fastag.balance -= amount
    
    txn_id = f"TOLL{uuid.uuid4().hex[:12].upper()}"
    
    transaction = FASTagTransaction(
        fastag_id=fastag.id,
        transaction_id=txn_id,
        amount=amount,
        type='toll_deduction',
        toll_name=toll['name'],
        location=toll['location'],
        balance_before=old_balance,
        balance_after=fastag.balance,
        status='completed'
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Toll deducted successfully!',
        'toll_name': toll['name'],
        'location': toll['location'],
        'amount': amount,
        'balance_before': old_balance,
        'balance_after': fastag.balance
    })

@fastag_bp.route('/fastag/transactions/<tag_id>')
@login_required
def fastag_transactions(tag_id):
    """View FASTag transactions"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    # Filter by type
    txn_type = request.args.get('type', 'all')
    query = FASTagTransaction.query.filter_by(fastag_id=fastag.id)
    
    if txn_type != 'all':
        query = query.filter_by(type=txn_type)
    
    transactions = query.order_by(FASTagTransaction.transaction_date.desc()).all()
    
    return render_template('fastag_transactions.html', 
                         fastag=fastag, 
                         transactions=transactions,
                         txn_type=txn_type)

@fastag_bp.route('/fastag/block/<tag_id>', methods=['POST'])
@login_required
def block_fastag(tag_id):
    """Block FASTag"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    fastag.status = 'blocked'
    db.session.commit()
    
    flash('FASTag blocked successfully!', 'success')
    return redirect(url_for('fastag.fastag_dashboard'))

@fastag_bp.route('/fastag/activate/<tag_id>', methods=['POST'])
@login_required
def activate_fastag(tag_id):
    """Activate FASTag"""
    fastag = FASTag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    
    fastag.status = 'active'
    db.session.commit()
    
    flash('FASTag activated successfully!', 'success')
    return redirect(url_for('fastag.fastag_dashboard'))
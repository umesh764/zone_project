from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.models import db, Bill
import uuid
from datetime import datetime

bills_bp = Blueprint('bills', __name__)

# ... rest of your code

@bills_bp.route('/electricity', methods=['GET', 'POST'])
@login_required
def electricity():
    if request.method == 'POST':
        consumer_number = request.form.get('consumer_number')
        operator = request.form.get('operator')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"EB{uuid.uuid4().hex[:12].upper()}"
        
        # Save bill to database
        bill = Bill(
            user_id=current_user.id,
            bill_type='electricity',
            consumer_number=consumer_number,
            operator=operator,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=amount,
            upi_id='bill@payment',
            transaction_id=transaction_id,
            status='completed',
            payment_method='bill_payment'
        )
        db.session.add(payment)
        db.session.commit()
        
        flash(f'Electricity bill of ₹{amount} paid successfully! Transaction ID: {transaction_id}', 'success')
        return redirect(url_for('bills.bill_history'))
    
    operators = [
        'MSEDCL - Maharashtra',
        'Tata Power - Mumbai',
        'Adani Electricity - Mumbai',
        'BEST - Mumbai',
        'Torrent Power - Gujarat',
        'UPPCL - Uttar Pradesh',
        'BSES - Delhi',
        'TPDDL - Delhi',
        'CESC - Kolkata',
        'WBSEDCL - West Bengal',
        'TSSPDCL - Telangana',
        'APEPDCL - Andhra Pradesh',
        'KSEB - Kerala',
        'BESCOM - Karnataka',
        'TANGEDCO - Tamil Nadu',
        'MPPKVVCL - Madhya Pradesh',
        'JVVNL - Rajasthan',
        'DHBVN - Haryana',
        'UPCL - Uttarakhand',
        'HPSEB - Himachal Pradesh',
        'JSEB - Jharkhand',
        'BSEB - Bihar',
        'OPGC - Odisha',
        'AESL - Assam',
        'PED - Punjab',
        'Goa Electricity',
        'Puducherry Electricity',
        'Chandigarh Electricity'
    ]
    return render_template('electricity.html', operators=operators)    
    # Get operators list
    operators = ['Tata Power', 'Adani Electricity', 'Torrent Power', 'BSES', 'MSEDCL', 'UPPCL']
    return render_template('electricity.html', operators=operators)

# Water Bill
@bills_bp.route('/water', methods=['GET', 'POST'])
@login_required
def water():
    if request.method == 'POST':
        consumer_number = request.form.get('consumer_number')
        operator = request.form.get('operator')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"WB{uuid.uuid4().hex[:12].upper()}"
        
        bill = WaterBill(
            user_id=current_user.id,
            consumer_number=consumer_number,
            operator=operator,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        flash(f'Water bill of ₹{amount} paid successfully!', 'success')
        return redirect(url_for('bills.bill_history', bill_type='water'))
    
    operators = ['MCGM', 'BMC', 'Delhi Jal Board', 'Chennai Metro Water', 'Bangalore Water Supply']
    return render_template('water.html', operators=operators)
# Loans
@bills_bp.route('/loans', methods=['GET', 'POST'])
@login_required
def loans():
    if request.method == 'POST':
        loan_type = request.form.get('loan_type')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"LOAN{uuid.uuid4().hex[:12].upper()}"
        
        bill = Bill(
            user_id=current_user.id,
            bill_type='loan',
            consumer_number=loan_type,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        flash(f'Loan payment of ₹{amount} successful!', 'success')
        return redirect(url_for('bills.bill_history'))
    
    loan_types = ['Home Loan', 'Car Loan', 'Personal Loan', 'Education Loan', 'Business Loan']
    return render_template('loans.html', loan_types=loan_types)

# Property Tax
@bills_bp.route('/property-tax', methods=['GET', 'POST'])
@login_required
def property_tax():
    if request.method == 'POST':
        property_id = request.form.get('property_id')
        assessment_number = request.form.get('assessment_number')
        zone = request.form.get('zone')
        amount = float(request.form.get('amount'))
        financial_year = request.form.get('financial_year')
        
        transaction_id = f"PTX{uuid.uuid4().hex[:12].upper()}"
        
        tax = PropertyTax(
            user_id=current_user.id,
            property_id=property_id,
            assessment_number=assessment_number,
            zone=zone,
            amount=amount,
            financial_year=financial_year,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(tax)
        db.session.commit()
        
        flash(f'Property tax of ₹{amount} paid successfully!', 'success')
        return redirect(url_for('bills.bill_history', bill_type='property'))
    
    zones = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']
    years = [f"{y}-{y+1}" for y in range(2020, 2026)]
    return render_template('property_tax.html', zones=zones, years=years)

# Gas Bill
@bills_bp.route('/gas', methods=['GET', 'POST'])
@login_required
def gas():
    if request.method == 'POST':
        consumer_number = request.form.get('consumer_number')
        operator = request.form.get('operator')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"GAS{uuid.uuid4().hex[:12].upper()}"
        
        bill = GasBill(
            user_id=current_user.id,
            consumer_number=consumer_number,
            operator=operator,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        flash(f'Gas bill of ₹{amount} paid successfully!', 'success')
        return redirect(url_for('bills.bill_history', bill_type='gas'))
    
    operators = ['Mahanagar Gas', 'Gujarat Gas', 'Adani Gas', 'IGL', 'GAIL']
    return render_template('gas.html', operators=operators)

# Internet Bill
@bills_bp.route('/internet', methods=['GET', 'POST'])
@login_required
def internet():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        operator = request.form.get('operator')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"NET{uuid.uuid4().hex[:12].upper()}"
        
        bill = InternetBill(
            user_id=current_user.id,
            customer_id=customer_id,
            operator=operator,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        flash(f'Internet bill of ₹{amount} paid successfully!', 'success')
        return redirect(url_for('bills.bill_history', bill_type='internet'))
    
    operators = ['JioFiber', 'Airtel Xstream', 'ACT Fibernet', 'Hathway', 'Tata Play']
    return render_template('internet.html', operators=operators)

# Credit Card Bill
@bills_bp.route('/credit-card', methods=['GET', 'POST'])
@login_required
def credit_card():
    if request.method == 'POST':
        card_number = request.form.get('card_number')[-4:]  # Last 4 digits
        bank_name = request.form.get('bank_name')
        amount = float(request.form.get('amount'))
        
        transaction_id = f"CC{uuid.uuid4().hex[:12].upper()}"
        
        bill = CreditCardBill(
            user_id=current_user.id,
            card_number=f"XXXX-XXXX-XXXX-{card_number}",
            bank_name=bank_name,
            amount=amount,
            transaction_id=transaction_id,
            status='completed',
            payment_date=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        
        flash(f'Credit card bill of ₹{amount} paid successfully!', 'success')
        return redirect(url_for('bills.bill_history', bill_type='credit_card'))
    
    banks = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Kotak', 'Yes Bank', 'Citi', 'American Express']
    return render_template('credit_card.html', banks=banks)

# Bill History
@bills_bp.route('/bill-history')
@login_required
def bill_history():
    bill_type = request.args.get('bill_type', 'all')
    
    # Fetch all bills
    electricity = Bill.query.filter_by(user_id=current_user.id, bill_type='electricity').all()
    water = WaterBill.query.filter_by(user_id=current_user.id).all()
    property_tax = PropertyTax.query.filter_by(user_id=current_user.id).all()
    gas = GasBill.query.filter_by(user_id=current_user.id).all()
    internet = InternetBill.query.filter_by(user_id=current_user.id).all()
    credit_card = CreditCardBill.query.filter_by(user_id=current_user.id).all()
    
    # Combine all bills with type
    all_bills = []
    
    for bill in electricity:
        all_bills.append({
            'id': bill.id,
            'type': 'Electricity',
            'consumer_no': bill.consumer_number,
            'operator': bill.operator,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    for bill in water:
        all_bills.append({
            'id': bill.id,
            'type': 'Water',
            'consumer_no': bill.consumer_number,
            'operator': bill.operator,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    for bill in property_tax:
        all_bills.append({
            'id': bill.id,
            'type': 'Property Tax',
            'property_id': bill.property_id,
            'zone': bill.zone,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    for bill in gas:
        all_bills.append({
            'id': bill.id,
            'type': 'Gas',
            'consumer_no': bill.consumer_number,
            'operator': bill.operator,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    for bill in internet:
        all_bills.append({
            'id': bill.id,
            'type': 'Internet',
            'customer_id': bill.customer_id,
            'operator': bill.operator,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    for bill in credit_card:
        all_bills.append({
            'id': bill.id,
            'type': 'Credit Card',
            'card_number': bill.card_number,
            'bank': bill.bank_name,
            'amount': bill.amount,
            'date': bill.payment_date,
            'transaction_id': bill.transaction_id,
            'status': bill.status
        })
    
    # Sort by date (newest first)
    all_bills.sort(key=lambda x: x['date'], reverse=True)
    
    # Filter by type if needed
    if bill_type != 'all':
        type_map = {
            'electricity': 'Electricity',
            'water': 'Water',
            'property': 'Property Tax',
            'gas': 'Gas',
            'internet': 'Internet',
            'credit_card': 'Credit Card'
        }
        filtered_type = type_map.get(bill_type, '')
        all_bills = [b for b in all_bills if b['type'] == filtered_type]
    
    return render_template('bill_history.html', bills=all_bills, current_type=bill_type)
# Search Electricity Bill
@bills_bp.route('/search-electricity', methods=['POST'])
@login_required
def search_electricity():
    data = request.json
    consumer_number = data.get('consumer_number')
    
    # Mock database - यहाँ आप real API से connect कर सकते हैं
    mock_data = {
        '123456': {'name': 'Ramesh Kumar', 'address': '123, MG Road, Mumbai', 'amount': 1250, 'due_date': '2024-03-15', 'bill_number': 'EB202402001'},
        '789012': {'name': 'Suresh Patel', 'address': '45, Gandhi Nagar, Delhi', 'amount': 2340, 'due_date': '2024-03-20', 'bill_number': 'EB202402002'},
        '345678': {'name': 'Amit Sharma', 'address': '78, Park Street, Kolkata', 'amount': 3450, 'due_date': '2024-03-10', 'bill_number': 'EB202402003'},
    }
    
    if consumer_number in mock_data:
        return jsonify({'success': True, 'data': mock_data[consumer_number]})
    else:
        return jsonify({'success': False, 'message': 'Consumer number not found'})

# Search Water Bill
@bills_bp.route('/search-water', methods=['POST'])
@login_required
def search_water():
    data = request.json
    consumer_number = data.get('consumer_number')
    
    mock_data = {
        'WAT123': {'name': 'Ramesh Kumar', 'address': '123, MG Road, Mumbai', 'amount': 850, 'due_date': '2024-03-18', 'bill_number': 'WB202402001'},
        'WAT456': {'name': 'Suresh Patel', 'address': '45, Gandhi Nagar, Delhi', 'amount': 1200, 'due_date': '2024-03-22', 'bill_number': 'WB202402002'},
        'WAT789': {'name': 'Priya Singh', 'address': '12, Civil Lines, Lucknow', 'amount': 675, 'due_date': '2024-03-25', 'bill_number': 'WB202402003'},
    }
    
    if consumer_number in mock_data:
        return jsonify({'success': True, 'data': mock_data[consumer_number]})
    else:
        return jsonify({'success': False, 'message': 'Consumer number not found'})

# Search Gas Bill
@bills_bp.route('/search-gas', methods=['POST'])
@login_required
def search_gas():
    data = request.json
    consumer_number = data.get('consumer_number')
    
    mock_data = {
        'GAS123': {'name': 'Amit Sharma', 'address': '78, Park Street, Kolkata', 'amount': 1450, 'due_date': '2024-03-12', 'bill_number': 'GB202402001'},
        'GAS456': {'name': 'Neha Gupta', 'address': '34, Model Town, Delhi', 'amount': 980, 'due_date': '2024-03-28', 'bill_number': 'GB202402002'},
        'GAS789': {'name': 'Rajesh Kumar', 'address': '56, Jayanagar, Bangalore', 'amount': 2100, 'due_date': '2024-03-05', 'bill_number': 'GB202402003'},
    }
    
    if consumer_number in mock_data:
        return jsonify({'success': True, 'data': mock_data[consumer_number]})
    else:
        return jsonify({'success': False, 'message': 'Consumer number not found'})

# Search Internet Bill
@bills_bp.route('/search-internet', methods=['POST'])
@login_required
def search_internet():
    data = request.json
    customer_id = data.get('customer_id')
    
    mock_data = {
        'JIO123': {'name': 'Priya Singh', 'plan': 'JioFiber 100Mbps', 'amount': 849, 'due_date': '2024-03-15', 'bill_number': 'IN202402001'},
        'AIR456': {'name': 'Amit Sharma', 'plan': 'Airtel Xstream 200Mbps', 'amount': 1199, 'due_date': '2024-03-20', 'bill_number': 'IN202402002'},
        'ACT789': {'name': 'Suresh Patel', 'plan': 'ACT Fibernet 150Mbps', 'amount': 999, 'due_date': '2024-03-10', 'bill_number': 'IN202402003'},
    }
    
    if customer_id in mock_data:
        return jsonify({'success': True, 'data': mock_data[customer_id]})
    else:
        return jsonify({'success': False, 'message': 'Customer ID not found'})

# Search Property Tax
@bills_bp.route('/search-property', methods=['POST'])
@login_required
def search_property():
    data = request.json
    property_id = data.get('property_id')
    
    mock_data = {
        'PTX001': {'name': 'Ramesh Kumar', 'address': '123, MG Road, Mumbai', 'zone': 'Zone 3', 'amount': 12500, 'due_date': '2024-06-30', 'assessment_year': '2023-24'},
        'PTX002': {'name': 'Suresh Patel', 'address': '45, Gandhi Nagar, Delhi', 'zone': 'Zone 5', 'amount': 18750, 'due_date': '2024-06-30', 'assessment_year': '2023-24'},
        'PTX003': {'name': 'Amit Sharma', 'address': '78, Park Street, Kolkata', 'zone': 'Zone 2', 'amount': 22300, 'due_date': '2024-06-30', 'assessment_year': '2023-24'},
    }
    
    if property_id in mock_data:
        return jsonify({'success': True, 'data': mock_data[property_id]})
    else:
        return jsonify({'success': False, 'message': 'Property ID not found'})

# Search Credit Card Bill
@bills_bp.route('/search-credit-card', methods=['POST'])
@login_required
def search_credit_card():
    data = request.json
    card_number = data.get('card_number')
    
    mock_data = {
        '1234': {'bank': 'HDFC', 'name': 'Ramesh Kumar', 'amount': 15400, 'due_date': '2024-03-25', 'min_due': 5000},
        '5678': {'bank': 'SBI', 'name': 'Suresh Patel', 'amount': 28750, 'due_date': '2024-03-18', 'min_due': 10000},
        '9012': {'bank': 'ICICI', 'name': 'Amit Sharma', 'amount': 43200, 'due_date': '2024-03-30', 'min_due': 15000},
    }
    
    if card_number in mock_data:
        return jsonify({'success': True, 'data': mock_data[card_number]})
    else:
        return jsonify({'success': False, 'message': 'Card number not found'})

# Bill receipt
@bills_bp.route('/bill-receipt/<bill_type>/<int:bill_id>')
@login_required
def bill_receipt(bill_type, bill_id):
    if bill_type == 'electricity':
        bill = ElectricityBill.query.get_or_404(bill_id)
    elif bill_type == 'water':
        bill = WaterBill.query.get_or_404(bill_id)
    elif bill_type == 'property':
        bill = PropertyTax.query.get_or_404(bill_id)
    elif bill_type == 'gas':
        bill = GasBill.query.get_or_404(bill_id)
    elif bill_type == 'internet':
        bill = InternetBill.query.get_or_404(bill_id)
    elif bill_type == 'credit_card':
        bill = CreditCardBill.query.get_or_404(bill_id)
    else:
        flash('Invalid bill type', 'error')
        return redirect(url_for('bills.bill_history'))
    
    # Check if bill belongs to current user
    if bill.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('bills.bill_history'))
    
    return render_template('bill_receipt.html', bill=bill, bill_type=bill_type)

# Quick pay bill (from saved bills)
@bills_bp.route('/quick-pay-bill', methods=['POST'])
@login_required
def quick_pay_bill():
    bill_type = request.form.get('bill_type')
    bill_id = int(request.form.get('bill_id'))
    
    if bill_type == 'electricity':
        bill = ElectricityBill.query.get(bill_id)
    elif bill_type == 'water':
        bill = WaterBill.query.get(bill_id)
    # ... similar for other types
    
    if bill and bill.user_id == current_user.id:
        # Generate new transaction
        new_transaction = f"PAY{uuid.uuid4().hex[:12].upper()}"
        bill.transaction_id = new_transaction
        bill.status = 'completed'
        bill.payment_date = datetime.utcnow()
        db.session.commit()
        
        flash(f'Bill paid successfully! Transaction ID: {new_transaction}', 'success')
    
    return redirect(url_for('bills.bill_history'))
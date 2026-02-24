from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from modules.models import db, Payment, User, SIP, Gold, Silver, Recharge, Bill, Loan, LoanPayment
import qrcode
import uuid
import os
import re
from datetime import datetime, timedelta
import base64
from io import BytesIO

payment_bp = Blueprint('payment', __name__)

# UPI Apps mapping
UPI_APPS = {
    'googlepay': 'tez',
    'phonepe': 'phonepe',
    'paytm': 'paytm',
    'bhim': 'bhim',
    'amazonpay': 'amazonpay'
}

def validate_upi_id(upi_id):
    """Validate UPI ID format"""
    pattern = r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$'
    return re.match(pattern, upi_id)

def get_upi_from_mobile(mobile):
    """Get possible UPI IDs from mobile number"""
    # Common UPI handles for mobile numbers
    handles = ['@okhdfcbank', '@okaxis', '@ybl', '@paytm', '@ibl', '@axl']
    upi_ids = [f"{mobile}{handle}" for handle in handles]
    return upi_ids

def generate_upi_qr(upi_id, amount=0, name="Zone Pay", note="Payment"):
    """Generate UPI QR code"""
    if amount and amount > 0:
        # Payment QR
        upi_string = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&tn={note}&cu=INR"
    else:
        # Collect QR (just UPI ID)
        upi_string = f"upi://pay?pa={upi_id}&pn={name}&cu=INR"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for web display
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

@payment_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        payment_type = request.form.get('payment_type', 'qr')
        
        if payment_type == 'mobile':
            # Mobile number se payment
            mobile = request.form.get('mobile')
            amount = float(request.form.get('amount'))
            note = request.form.get('note', 'Payment')
            
            # Get UPI IDs from mobile
            upi_ids = get_upi_from_mobile(mobile)
            
            return render_template('select_upi.html', 
                                 upi_ids=upi_ids,
                                 mobile=mobile,
                                 amount=amount,
                                 note=note)
        
        elif payment_type == 'upi':
            # Direct UPI ID se payment
            upi_id = request.form.get('upi_id')
            amount = float(request.form.get('amount'))
            note = request.form.get('note', 'Payment')
            
            if not validate_upi_id(upi_id):
                flash('Invalid UPI ID format', 'error')
                return redirect(url_for('payment.payment'))
            
            # Generate QR code
            qr_base64 = generate_upi_qr(upi_id, amount, current_user.name, note)
            
            # Create transaction
            transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
            payment = Payment(
                user_id=current_user.id,
                amount=amount,
                upi_id=upi_id,
                transaction_id=transaction_id,
                status='pending',
                payment_method='upi_qr'
            )
            db.session.add(payment)
            db.session.commit()
            
            # Store in session
            session['current_payment'] = {
                'id': payment.id,
                'amount': amount,
                'upi_id': upi_id,
                'transaction_id': transaction_id,
                'qr_base64': qr_base64,
                'note': note
            }
            
            return redirect(url_for('payment.scan_pay'))
        
        elif payment_type == 'qr_scan':
            # QR code scan
            return render_template('scan_qr.html')
    
    return render_template('payment.html')

@payment_bp.route('/process-upi', methods=['POST'])
@login_required
def process_upi():
    """Process UPI payment after user selects UPI ID"""
    upi_id = request.form.get('upi_id')
    amount = float(request.form.get('amount'))
    note = request.form.get('note', 'Payment')
    mobile = request.form.get('mobile')
    
    # Generate QR code
    qr_base64 = generate_upi_qr(upi_id, amount, current_user.name, note)
    
    # Create transaction
    transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
    payment = Payment(
        user_id=current_user.id,
        amount=amount,
        upi_id=upi_id,
        transaction_id=transaction_id,
        status='pending',
        payment_method='upi_qr'
    )
    db.session.add(payment)
    db.session.commit()
    
    # Store in session
    session['current_payment'] = {
        'id': payment.id,
        'amount': amount,
        'upi_id': upi_id,
        'transaction_id': transaction_id,
        'qr_base64': qr_base64,
        'note': note,
        'mobile': mobile
    }
    
    return redirect(url_for('payment.scan_pay'))

@payment_bp.route('/scan-qr', methods=['POST'])
@login_required
def scan_qr():
    """Process scanned QR code"""
    data = request.json
    qr_data = data.get('qr_data')
    
    # Parse UPI QR data
    # Format: upi://pay?pa=upi_id&pn=name&am=amount&tn=note
    import urllib.parse
    parsed = urllib.parse.urlparse(qr_data)
    params = urllib.parse.parse_qs(parsed.query)
    
    upi_id = params.get('pa', [None])[0]
    amount = params.get('am', [0])[0]
    note = params.get('tn', ['Payment'])[0]
    
    if not upi_id:
        return jsonify({'success': False, 'error': 'Invalid QR code'})
    
    return jsonify({
        'success': True,
        'upi_id': upi_id,
        'amount': float(amount) if amount else 0,
        'note': note
    })

@payment_bp.route('/scan-pay')
@login_required
def scan_pay():
    payment_data = session.get('current_payment')
    if not payment_data:
        return redirect(url_for('payment.payment'))
    
    return render_template('scan-pay.html', payment=payment_data)

@payment_bp.route('/verify-payment/<transaction_id>')
@login_required
def verify_payment(transaction_id):
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    if payment:
        # In real app, check with bank API
        # For demo, we'll mark as success
        payment.status = 'success'
        
        # Generate receipt
        receipt_path = generate_receipt(payment)
        payment.receipt_path = receipt_path
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'transaction_id': payment.transaction_id,
            'amount': payment.amount,
            'upi_id': payment.upi_id,
            'receipt': receipt_path
        })
    
    return jsonify({'status': 'failed'})

def generate_receipt(payment):
    """Generate payment receipt"""
    receipt_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Receipt - Zone</title>
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .receipt {{
                max-width: 500px;
                margin: auto;
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }}
            .receipt::before {{
                content: '🧡 ZONE';
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 40px;
                opacity: 0.1;
                transform: rotate(-15deg);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h2 {{
                color: #FF6B35;
                margin-bottom: 10px;
            }}
            .success-icon {{
                font-size: 60px;
                color: #28a745;
                margin-bottom: 20px;
            }}
            .details {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
            }}
            .row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px dashed #dee2e6;
            }}
            .row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: 600;
                color: #495057;
            }}
            .value {{
                font-weight: 700;
                color: #FF6B35;
            }}
            .amount {{
                font-size: 24px;
                color: #28a745;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #6c757d;
                font-size: 14px;
            }}
            .qr-mini {{
                text-align: center;
                margin: 20px 0;
            }}
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                .receipt {{
                    box-shadow: none;
                    border: 2px solid #FF6B35;
                }}
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="receipt">
            <div class="header">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h2>Payment Successful!</h2>
                <p>Transaction Completed</p>
            </div>
            
            <div class="details">
                <div class="row">
                    <span class="label"><i class="fas fa-hashtag"></i> Transaction ID:</span>
                    <span class="value">{payment.transaction_id}</span>
                </div>
                <div class="row">
                    <span class="label"><i class="fas fa-calendar"></i> Date & Time:</span>
                    <span class="value">{payment.created_at.strftime('%d-%m-%Y %H:%M')}</span>
                </div>
                <div class="row">
                    <span class="label"><i class="fas fa-user"></i> Paid To:</span>
                    <span class="value">{payment.upi_id}</span>
                </div>
                <div class="row">
                    <span class="label"><i class="fas fa-credit-card"></i> Payment Method:</span>
                    <span class="value">UPI QR</span>
                </div>
                <div class="row">
                    <span class="label"><i class="fas fa-info-circle"></i> Status:</span>
                    <span class="value" style="color: #28a745;">SUCCESS</span>
                </div>
                <div class="row">
                    <span class="label"><i class="fas fa-rupee-sign"></i> Amount:</span>
                    <span class="amount">₹{payment.amount:.2f}</span>
                </div>
            </div>
            
            <div class="qr-mini">
                <i class="fas fa-qrcode" style="font-size: 50px; color: #FF6B35;"></i>
                <p>Scan to verify</p>
            </div>
            
            <div class="footer">
                <p>This is a computer generated receipt</p>
                <p><i class="fas fa-bolt"></i> Powered by Zone Pay</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = f"receipt_{payment.transaction_id}.html"
    filepath = os.path.join('static/receipts', filename)
    
    os.makedirs('static/receipts', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(receipt_html)
    
    return filename

@payment_bp.route('/receipt/<transaction_id>')
@login_required
def receipt(transaction_id):
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    if payment and payment.user_id == current_user.id:
        return render_template('receipt.html', payment=payment)
    return redirect(url_for('payment.dashboard'))

@payment_bp.route('/dashboard')
@login_required
def dashboard():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template('dashboard.html', payments=payments)
# QR Code Upload Payment
@payment_bp.route('/upload-qr', methods=['POST'])
@login_required
def upload_qr():
    if 'qr_image' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('payment.payment'))
    
    file = request.files['qr_image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('payment.payment'))
    
    if file:
        # Save uploaded QR
        filename = f"qr_upload_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join('static/uploads', filename)
        os.makedirs('static/uploads', exist_ok=True)
        file.save(filepath)
        
        # Here you would parse QR code and extract UPI ID
        # For demo, we'll simulate
        upi_id = request.form.get('upi_id', 'user@okhdfcbank')
        amount = float(request.form.get('amount', 0))
        note = request.form.get('note', 'QR Payment')
        
        # Generate payment QR
        qr_base64 = generate_upi_qr(upi_id, amount, current_user.name, note)
        
        # Create transaction
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        payment = Payment(
            user_id=current_user.id,
            amount=amount,
            upi_id=upi_id,
            transaction_id=transaction_id,
            status='pending',
            payment_method='qr_upload',
            qr_uploaded=filename
        )
        db.session.add(payment)
        db.session.commit()
        
        session['current_payment'] = {
            'id': payment.id,
            'amount': amount,
            'upi_id': upi_id,
            'transaction_id': transaction_id,
            'qr_base64': qr_base64,
            'note': note
        }
        
        return redirect(url_for('payment.scan_pay'))

# Mutual Fund SIP
@payment_bp.route('/sip', methods=['GET', 'POST'])
@login_required
def sip():
    if request.method == 'POST':
        fund_name = request.form.get('fund_name')
        amount = float(request.form.get('amount'))
        frequency = request.form.get('frequency')
        
        sip = SIP(
            user_id=current_user.id,
            fund_name=fund_name,
            amount=amount,
            frequency=frequency,
            start_date=datetime.utcnow(),
            next_date=datetime.utcnow() + timedelta(days=30 if frequency=='monthly' else 90),
            status='active'
        )
        db.session.add(sip)
        db.session.commit()
        
        flash(f'SIP started in {fund_name} for ₹{amount}', 'success')
        return redirect(url_for('payment.sip_tracker'))
    
    # Get user's SIPs
    sips = SIP.query.filter_by(user_id=current_user.id).all()
    return render_template('sip.html', sips=sips)

@payment_bp.route('/sip-tracker')
@login_required
def sip_tracker():
    sips = SIP.query.filter_by(user_id=current_user.id).all()
    total_invested = sum(sip.total_invested for sip in sips)
    total_value = sum(sip.current_value for sip in sips)
    total_returns = total_value - total_invested
    
    return render_template('sip_tracker.html', 
                         sips=sips,
                         total_invested=total_invested,
                         total_value=total_value,
                         total_returns=total_returns)

# Gold Purchase
@payment_bp.route('/gold', methods=['GET', 'POST'])
@login_required
def gold():
    # Get current gold rate (in real app, fetch from API)
    current_rate = 6500  # per gram
    
    if request.method == 'POST':
        grams = float(request.form.get('grams'))
        amount = grams * current_rate
        
        gold = Gold(
            user_id=current_user.id,
            grams=grams,
            rate=current_rate,
            amount=amount,
            type='buy',
            status='completed'
        )
        db.session.add(gold)
        db.session.commit()
        
        # Generate certificate
        cert_path = generate_gold_certificate(gold)
        gold.certificate_path = cert_path
        db.session.commit()
        
        flash(f'Successfully purchased {grams}g Gold', 'success')
        return redirect(url_for('payment.gold_portfolio'))
    
    # Get user's gold holdings
    holdings = Gold.query.filter_by(user_id=current_user.id, type='buy').all()
    total_grams = sum(g.grams for g in holdings)
    total_value = sum(g.grams * current_rate for g in holdings)
    
    return render_template('gold.html', 
                         current_rate=current_rate,
                         holdings=holdings,
                         total_grams=total_grams,
                         total_value=total_value)

@payment_bp.route('/gold-portfolio')
@login_required
def gold_portfolio():
    holdings = Gold.query.filter_by(user_id=current_user.id, type='buy').all()
    current_rate = 6500
    total_grams = sum(g.grams for g in holdings)
    total_value = sum(g.grams * current_rate for g in holdings)
    
    return render_template('gold_portfolio.html',
                         holdings=holdings,
                         total_grams=total_grams,
                         total_value=total_value,
                         current_rate=current_rate)

# Silver Purchase
@payment_bp.route('/silver', methods=['GET', 'POST'])
@login_required
def silver():
    current_rate = 75  # per gram
    
    if request.method == 'POST':
        grams = float(request.form.get('grams'))
        amount = grams * current_rate
        
        silver = Silver(
            user_id=current_user.id,
            grams=grams,
            rate=current_rate,
            amount=amount,
            type='buy',
            status='completed'
        )
        db.session.add(silver)
        db.session.commit()
        
        flash(f'Successfully purchased {grams}g Silver', 'success')
        return redirect(url_for('payment.silver_portfolio'))
    
    holdings = Silver.query.filter_by(user_id=current_user.id, type='buy').all()
    total_grams = sum(s.grams for s in holdings)
    total_value = sum(s.grams * current_rate for s in holdings)
    
    return render_template('silver.html',
                         current_rate=current_rate,
                         holdings=holdings,
                         total_grams=total_grams,
                         total_value=total_value)

@payment_bp.route('/silver-portfolio')
@login_required
def silver_portfolio():
    holdings = Silver.query.filter_by(user_id=current_user.id, type='buy').all()
    current_rate = 75
    total_grams = sum(s.grams for s in holdings)
    total_value = sum(s.grams * current_rate for s in holdings)
    
    return render_template('silver_portfolio.html',
                         holdings=holdings,
                         total_grams=total_grams,
                         total_value=total_value,
                         current_rate=current_rate)

# Mobile Recharge
@payment_bp.route('/recharge', methods=['GET', 'POST'])
@login_required
def recharge():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        operator = request.form.get('operator')
        amount = float(request.form.get('amount'))
        recharge_type = request.form.get('type')
        
        # Generate transaction ID
        transaction_id = f"RCH{uuid.uuid4().hex[:12].upper()}"
        
        # Save recharge record
        recharge = Recharge(
            user_id=current_user.id,
            mobile=mobile,
            operator=operator,
            amount=amount,
            type=recharge_type,
            transaction_id=transaction_id,
            status='pending'
        )
        db.session.add(recharge)
        db.session.commit()
        
        # Redirect to company's payment page based on operator
        operator_links = {
            'Jio': 'https://www.jio.com/selfcare/recharge/',
            'Airtel': 'https://www.airtel.in/s/selfcare/recharge/',
            'Vi': 'https://www.myvi.in/recharge',
            'BSNL': 'https://portal2.bsnl.in/myportal/quickrecharge.do',
            'MTNL': 'https://www.mtnl.in/recharge.php'
        }
        
        # Get redirect URL or default to payment page
        redirect_url = operator_links.get(operator, f'/payment/process/{transaction_id}')
        
        flash(f'Redirecting to {operator} payment page...', 'info')
        return redirect(redirect_url)
    
    operators = ['Jio', 'Airtel', 'Vi', 'BSNL', 'MTNL']
    return render_template('recharge.html', operators=operators)

@payment_bp.route('/recharge-history')
@login_required
def recharge_history():
    recharges = Recharge.query.filter_by(user_id=current_user.id).order_by(Recharge.created_at.desc()).all()
    return render_template('recharge_history.html', recharges=recharges)

# Loan Repayment
@payment_bp.route('/loans', methods=['GET', 'POST'])
@login_required
def loans():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # Add new loan
            loan = Loan(
                user_id=current_user.id,
                loan_type=request.form.get('loan_type'),
                lender=request.form.get('lender'),
                account_number=request.form.get('account_number'),
                amount=float(request.form.get('amount')),
                emi_amount=float(request.form.get('emi_amount')),
                remaining=float(request.form.get('amount')),
                status='active'
            )
            db.session.add(loan)
            db.session.commit()
            flash('Loan added successfully', 'success')
            
        elif action == 'pay':
            # Pay EMI
            loan_id = int(request.form.get('loan_id'))
            amount = float(request.form.get('amount'))
            
            loan = Loan.query.get(loan_id)
            if loan and loan.user_id == current_user.id:
                transaction_id = f"LOAN{uuid.uuid4().hex[:12].upper()}"
                
                payment = LoanPayment(
                    loan_id=loan_id,
                    user_id=current_user.id,
                    amount=amount,
                    transaction_id=transaction_id,
                    status='completed'
                )
                db.session.add(payment)
                
                loan.total_paid += amount
                loan.remaining -= amount
                
                if loan.remaining <= 0:
                    loan.status = 'completed'
                
                db.session.commit()
                flash(f'EMI payment of ₹{amount} successful', 'success')
        
        return redirect(url_for('payment.loans'))
    
    loans = Loan.query.filter_by(user_id=current_user.id).all()
    payments = LoanPayment.query.filter_by(user_id=current_user.id).order_by(LoanPayment.payment_date.desc()).all()
    
    total_loan = sum(l.amount for l in loans)
    total_paid = sum(l.total_paid for l in loans)
    total_remaining = sum(l.remaining for l in loans if l.status == 'active')
    
    return render_template('loans.html',
                         loans=loans,
                         payments=payments,
                         total_loan=total_loan,
                         total_paid=total_paid,
                         total_remaining=total_remaining)

# Helper function for gold certificate
def generate_gold_certificate(gold):
    cert_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gold Certificate - Zone</title>
        <style>
            body {{ font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); }}
            .certificate {{ max-width: 800px; margin: 50px auto; background: white; padding: 40px; border: 10px solid #FFD700; border-radius: 20px; }}
            .header {{ text-align: center; }}
            .gold-seal {{ font-size: 60px; color: #FFD700; }}
            .content {{ margin: 30px 0; }}
            .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #ccc; }}
        </style>
    </head>
    <body>
        <div class="certificate">
            <div class="header">
                <div class="gold-seal">🥇</div>
                <h1>Digital Gold Certificate</h1>
            </div>
            <div class="content">
                <div class="row"><span>Certificate ID:</span> <span>GOLD{datetime.utcnow().strftime('%Y%m%d')}{gold.id}</span></div>
                <div class="row"><span>Owner:</span> <span>{gold.user.name}</span></div>
                <div class="row"><span>Gold (grams):</span> <span>{gold.grams}g</span></div>
                <div class="row"><span>Purchase Rate:</span> <span>₹{gold.rate}/g</span></div>
                <div class="row"><span>Total Amount:</span> <span>₹{gold.amount}</span></div>
                <div class="row"><span>Date:</span> <span>{gold.created_at.strftime('%d-%m-%Y')}</span></div>
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = f"gold_cert_{gold.id}.html"
    filepath = os.path.join('static/certificates', filename)
    os.makedirs('static/certificates', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cert_html)
    
    return filename

@payment_bp.route('/payment-history')
@login_required
def payment_history():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template('payment_history.html', payments=payments)

@payment_bp.route('/my-qr')
@login_required
def my_qr():
    """Generate user's own QR code for receiving payments"""
    # Get user's UPI IDs (you can store multiple in database)
    upi_ids = [
        f"{current_user.phone}@ybl",
        f"{current_user.phone}@okhdfcbank",
        f"{current_user.phone}@paytm"
    ]
    
    qr_codes = []
    for upi_id in upi_ids:
        qr_base64 = generate_upi_qr(upi_id)
        qr_codes.append({
            'upi_id': upi_id,
            'qr': qr_base64
        })
    
    return render_template('my_qr.html', qr_codes=qr_codes)

# Sell Gold Route
@payment_bp.route('/sell-gold/<int:gold_id>', methods=['POST'])
@login_required
def sell_gold(gold_id):
    gold = Gold.query.get_or_404(gold_id)
    if gold.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    # Mark as sold
    gold.type = 'sold'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Gold sold successfully'})

# Sell Silver Route
@payment_bp.route('/sell-silver/<int:silver_id>', methods=['POST'])
@login_required
def sell_silver(silver_id):
    silver = Silver.query.get_or_404(silver_id)
    if silver.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    silver.type = 'sold'
    db.session.commit()
# Live Gold Rate API
@payment_bp.route('/api/gold-rate')
@login_required
def gold_rate():
    import random
    from datetime import datetime
    
    # Base rate with some variation
    base_rate = 6500
    variation = random.randint(-50, 50)
    current_rate = base_rate + variation
    
    return jsonify({
        'rate': current_rate,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'change': variation,
        'change_percent': round((variation / base_rate) * 100, 2)
    })

# Live Silver Rate API
@payment_bp.route('/api/silver-rate')
@login_required
def silver_rate():
    import random
    from datetime import datetime
    
    base_rate = 75
    variation = random.randint(-2, 2)
    current_rate = base_rate + variation
    
    return jsonify({
        'rate': current_rate,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'change': variation,
        'change_percent': round((variation / base_rate) * 100, 2)
    })

# Real API Version (असली API से connect करने के लिए)

# @payment_bp.route('/api/gold-rate-real')
# @login_required
# def gold_rate_real():
#     import requests
#     try:
#         response = requests.get('https://www.goldapi.io/api/XAU/INR', 
#                                headers={'x-access-token': 'YOUR_API_KEY'})
#         data = response.json()
#         return jsonify({
#             'rate': data['price'],
#             'timestamp': data['timestamp'],
#             'change': data['ch'],
#             'change_percent': data['chp']
#         })
#     except Exception as e:
#         return jsonify({'error': str(e), 'rate': 6500})

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from extensions import limiter
from modules.models import db, User, OTPVerification
import random
import re
from datetime import datetime, timedelta

# Blueprint banayein
auth_bp = Blueprint('auth', __name__)

# Initialize extensions
bcrypt = Bcrypt()
login_manager = LoginManager()

# ⚠️ SIRF EK USER_LOADER HONA CHAHIYE
@login_manager.user_loader
def load_user(user_id):
    from modules.models import User
    return User.query.get(int(user_id))
    

# Helper function to send OTP
def send_otp_sms(phone, otp):
    print(f"Sending OTP {otp} to {phone}")
    return True

def generate_otp():
    return str(random.randint(100000, 999999))

def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not validate_phone(phone):
            flash('Please enter a valid 10-digit mobile number', 'error')
            return render_template('register.html')
        
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            flash('This phone number is already registered', 'error')
            return render_template('register.html')
        
        otp = generate_otp()
        
        otp_entry = OTPVerification(
            phone=phone,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_entry)
        db.session.commit()
        
        send_otp_sms(phone, otp)
        
        session['reg_phone'] = phone
        session['reg_name'] = name
        session['reg_email'] = email
        session['reg_password'] = bcrypt.generate_password_hash(password).decode('utf-8')
        
        flash(f'OTP sent to {phone}', 'success')
        return redirect(url_for('auth.verify_otp'))
    
    return render_template('register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        phone = session.get('reg_phone')
        
        otp_entry = OTPVerification.query.filter_by(
            phone=phone, 
            otp=otp,
            is_used=False
        ).first()
        
        if otp_entry and otp_entry.expires_at > datetime.utcnow():
            otp_entry.is_used = True
            
            user = User(
                phone=phone,
                name=session.get('reg_name'),
                email=session.get('reg_email'),
                password=session.get('reg_password'),
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            session.pop('reg_phone', None)
            session.pop('reg_name', None)
            session.pop('reg_email', None)
            session.pop('reg_password', None)
            
            login_user(user)
            
            flash('Registration successful! Welcome to Zone.', 'success')
            return redirect(url_for('payment.dashboard'))
        else:
            flash('Invalid or expired OTP', 'error')
    
    return render_template('verify-otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        user = User.query.filter_by(phone=phone).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('payment.dashboard'))
        else:
            flash('Invalid phone number or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-otp')
def resend_otp():
    phone = session.get('reg_phone')
    if phone:
        otp = generate_otp()
        
        otp_entry = OTPVerification(
            phone=phone,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_entry)
        db.session.commit()
        
        send_otp_sms(phone, otp)
        
        flash('New OTP sent successfully', 'success')
    return redirect(url_for('auth.verify_otp'))
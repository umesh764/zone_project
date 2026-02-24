from flask import Flask, render_template, session, redirect, request, url_for
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Sirf yahan se import karo
from modules.models import db

bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'zone-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zone.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Import blueprints (yahan import karo)
    from modules.auth import auth_bp
    from modules.payment import payment_bp
    from modules.travel import travel_bp
    from modules.fastag import fastag_bp      # ← ये line add करें
    from modules.rewards import rewards_bp 
    from modules.payment import payment_bp
    from modules.bills import bills_bp
    from modules.entertainment import entertainment_bp  # ← ये line add करें
    from modules.shopping import shopping_bp
    from modules.insurance import insurance_bp
    from modules.cibil import cibil_bp
    from modules.ott import ott_bp
    from modules.language import language_bp
   
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(fastag_bp)      # ← ये line add करें
    app.register_blueprint(rewards_bp)
    app.register_blueprint(travel_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(entertainment_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(insurance_bp)
    app.register_blueprint(cibil_bp)
    app.register_blueprint(ott_bp)
    app.register_blueprint(language_bp)
    
    # Routes
    @app.route('/')
    def index():
        return render_template('index.html', title='Zone Home')
    
    @app.route('/set-theme/<theme>')
    def set_theme(theme):
        if theme in ['orange', 'light', 'dark']:
            session['theme'] = theme
        return redirect(request.referrer or url_for('index'))
    
    @app.route('/about')
    def about():
        return render_template('about.html', title='About Zone')
    
    @app.route('/services')
    def services():
        return render_template('services.html', title='Our Services')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            flash(f'Thank you {name}! Your message has been sent!', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', title='Contact Zone')
    
    return app
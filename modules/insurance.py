from flask import Blueprint, render_template

insurance_bp = Blueprint('insurance', __name__)

# Insurance Home
@insurance_bp.route('/insurance')
def insurance_home():
    return render_template('insurance_home.html')

# Health Insurance
@insurance_bp.route('/insurance/health')
def health_insurance():
    return render_template('health_insurance.html')

# Life Insurance
@insurance_bp.route('/insurance/life')
def life_insurance():
    return render_template('life_insurance.html')

# Car Insurance
@insurance_bp.route('/insurance/car')
def car_insurance():
    return render_template('car_insurance.html')

# Bike Insurance
@insurance_bp.route('/insurance/bike')
def bike_insurance():
    return render_template('bike_insurance.html')

# Travel Insurance
@insurance_bp.route('/insurance/travel')
def travel_insurance():
    return render_template('travel_insurance.html')
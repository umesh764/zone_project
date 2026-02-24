from flask import Blueprint, render_template

cibil_bp = Blueprint('cibil', __name__)

@cibil_bp.route('/cibil')
def cibil_home():
    return render_template('cibil_home.html')

@cibil_bp.route('/cibil/check')
def cibil_check():
    return render_template('cibil_check.html')
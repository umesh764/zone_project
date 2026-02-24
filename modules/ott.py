from flask import Blueprint, render_template

ott_bp = Blueprint('ott', __name__)

@ott_bp.route('/entertainment/netflix')
def netflix():
    return render_template('netflix.html')

@ott_bp.route('/entertainment/prime')
def prime():
    return render_template('prime.html')

@ott_bp.route('/entertainment/hotstar')
def hotstar():
    return render_template('hotstar.html')

@ott_bp.route('/entertainment/spotify')
def spotify():
    return render_template('spotify.html')

@ott_bp.route('/entertainment/youtube')
def youtube():
    return render_template('youtube.html')
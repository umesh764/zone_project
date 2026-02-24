from flask import Blueprint, render_template
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    
    features = [
        {'icon': '📱', 'title': 'Mobile Ready', 'desc': 'Fully responsive design'},
        {'icon': '🎨', 'title': 'Orange Zone', 'desc': 'Beautiful orange theme'},
        {'icon': '🚀', 'title': 'Fast & Light', 'desc': 'Optimized performance'},
        {'icon': '🔒', 'title': 'Secure', 'desc': 'Your data is safe'}
    ]
    
    return render_template('index.html', 
                         title='Zone - Home',
                         welcome_message='Welcome to Zone!',
                         current_time=current_time,
                         features=features)

@main.route('/about')
def about():
    team_members = [
        {'name': 'Alex Zone', 'role': 'Founder', 'color': '#FF6B35'},
        {'name': 'Sarah Orange', 'role': 'Designer', 'color': '#F7934B'},
        {'name': 'Mike Gold', 'role': 'Developer', 'color': '#FFB347'}
    ]
    return render_template('about.html', title='About Zone', team=team_members)
@main.route('/set-theme/<theme>')
def set_theme(theme):
    # यहाँ आप session में theme save कर सकते हैं
    from flask import session, redirect, request
    session['theme'] = theme
    # पेज को पिछली जगह redirect करें
    return redirect(request.referrer or url_for('main.index'))


@main.route('/services')
def services():
    services_list = [
        {'name': 'Web Development', 'price': '$499', 'duration': '2 weeks', 'color': '#FF8C42'},
        {'name': 'Mobile Apps', 'price': '$799', 'duration': '3 weeks', 'color': '#FF6B35'},
        {'name': 'UI/UX Design', 'price': '$399', 'duration': '1 week', 'color': '#F97316'},
        {'name': 'Consulting', 'price': '$149/hr', 'duration': 'Flexible', 'color': '#FB8B24'}
    ]
    return render_template('services.html', title='Our Services', services=services_list)

@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Zone')

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='Page Not Found'), 404

from flask import Blueprint, render_template, request, jsonify
from modules.models import db, GovernmentDepartment
from sqlalchemy import or_

gov_bp = Blueprint('gov', __name__, url_prefix='/gov')

@gov_bp.route('/')
def home():
    """मेरी सरकार का होम पेज"""
    # सभी यूनिक कैटेगरी और सब-कैटेगरी डैशबोर्ड के लिए लाएँ
    categories = db.session.query(GovernmentDepartment.category).distinct().all()
    states = db.session.query(GovernmentDepartment.state).distinct().all()
    return render_template('gov/home.html', categories=[c[0] for c in categories if c[0]], states=[s[0] for s in states if s[0]])

@gov_bp.route('/search')
def search():
    """AI-लाइक सर्च एंडपॉइंट"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # डेटाबेस में नाम, विवरण और टैग्स में सर्च करें
    results = GovernmentDepartment.query.filter(
        GovernmentDepartment.is_active == True
    ).filter(
        or_(
            GovernmentDepartment.name.ilike(f'%{query}%'),
            GovernmentDepartment.description.ilike(f'%{query}%'),
            GovernmentDepartment.search_tags.ilike(f'%{query}%'),
            GovernmentDepartment.category.ilike(f'%{query}%'),
            GovernmentDepartment.sub_category.ilike(f'%{query}%'),
            GovernmentDepartment.parent_ministry.ilike(f'%{query}%'),
            GovernmentDepartment.state.ilike(f'%{query}%'),
            GovernmentDepartment.city.ilike(f'%{query}%')
        )
    ).limit(20).all()

    # JSON रिस्पॉन्स बनाएँ
    result_list = [{
        'id': dept.id,
        'name': dept.name,
        'category': dept.category,
        'sub_category': dept.sub_category,
        'parent_ministry': dept.parent_ministry,
        'state': dept.state,
        'city': dept.city,
        'website_url': dept.website_url,
        'logo_url': dept.logo_url
    } for dept in results]
    
    return jsonify(result_list)

@gov_bp.route('/department/<int:dept_id>')
def department_detail(dept_id):
    """किसी एक विभाग का डिटेल पेज"""
    dept = GovernmentDepartment.query.get_or_404(dept_id)
    return render_template('gov/department.html', dept=dept)

@gov_bp.route('/category/<string:category_name>')
def category_view(category_name):
    """कैटेगरी के हिसाब से सभी विभाग दिखाएँ"""
    page = request.args.get('page', 1, type=int)
    departments = GovernmentDepartment.query.filter_by(category=category_name, is_active=True).paginate(page=page, per_page=20)
    return render_template('gov/category.html', departments=departments, category_name=category_name)

@gov_bp.route('/state/<string:state_name>')
def state_view(state_name):
    """राज्य के हिसाब से सभी विभाग दिखाएँ"""
    page = request.args.get('page', 1, type=int)
    departments = GovernmentDepartment.query.filter_by(state=state_name, is_active=True).paginate(page=page, per_page=20)
    return render_template('gov/state.html', departments=departments, state_name=state_name)
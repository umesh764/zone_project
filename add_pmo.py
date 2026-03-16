from app import create_app
from modules.models import db, GovernmentDepartment

app = create_app()
with app.app_context():
    dept = GovernmentDepartment(
        name='प्रधानमंत्री कार्यालय',
        description='भारत के प्रधानमंत्री का आधिकारिक कार्यालय',
        website_url='https://pmindia.gov.in',
        category='केंद्र सरकार',
        sub_category='मंत्रालय',
        search_tags='pmo, pm, प्रधानमंत्री, prime minister'
    )
    db.session.add(dept)
    db.session.commit()
    print('✅ 1 department added successfully!')
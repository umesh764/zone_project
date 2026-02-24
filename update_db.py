from app import create_app, db
from modules.models import *

print("="*50)
print("🔄 Zone Pay Database Update")
print("="*50)

try:
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created/updated successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tables in database: {tables}")
        
        # Count records in each table
        print("\n📈 Record counts:")
        if 'user' in tables:
            print(f"   - Users: {User.query.count()}")
        if 'payment' in tables:
            print(f"   - Payments: {Payment.query.count()}")
        if 'sip' in tables:
            print(f"   - SIPs: {SIP.query.count()}")
        if 'gold' in tables:
            print(f"   - Gold: {Gold.query.count()}")
        if 'silver' in tables:
            print(f"   - Silver: {Silver.query.count()}")
        if 'recharge' in tables:
            print(f"   - Recharges: {Recharge.query.count()}")
        if 'loan' in tables:
            print(f"   - Loans: {Loan.query.count()}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("="*50)
input("Press Enter to exit...")
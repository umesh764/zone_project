from app import create_app, db
from modules.models import *
import os

print("="*50)
print("ZONE PAY - DATABASE RESET")
print("="*50)

# Delete old database file
db_path = 'instance/zone.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("Old database deleted.")

app = create_app()
with app.app_context():
    # Create new tables
    db.create_all()
    print("New database created with all tables.")
    
    # Check tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    
    # Check payment table columns
    if 'payment' in tables:
        columns = [col['name'] for col in inspector.get_columns('payment')]
        print("Payment table columns:", columns)
        if 'qr_uploaded' in columns:
            print("SUCCESS: qr_uploaded column exists!")
        else:
            print("ERROR: qr_uploaded column missing!")

print("="*50)
print("Database reset complete!")
print("="*50)
input("Press Enter to exit...")
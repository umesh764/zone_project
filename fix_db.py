from app import create_app, db
from modules.models import User, Payment, OTPVerification
from flask_bcrypt import Bcrypt
import sys

print("="*50)
print("🔧 Zone Pay Database Setup")
print("="*50)

try:
    app = create_app()
    with app.app_context():
        # Drop all tables
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("🏗️  Creating new tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Create test user
        print("👤 Creating test user...")
        bcrypt = Bcrypt(app)
        test_user = User(
            phone="9999999999",
            name="Test User",
            email="test@example.com",
            password=bcrypt.generate_password_hash("password123").decode('utf-8'),
            is_verified=True
        )
        db.session.add(test_user)
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ SUCCESS!")
        print("📱 Test User Created:")
        print("   Phone: 9999999999")
        print("   Password: password123")
        print("="*50)
        
except Exception as e:
    print("❌ Error:", e)
    
input("\nPress Enter to exit...")
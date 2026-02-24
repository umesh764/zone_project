import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zone-super-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///zone.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # UPI Configuration
    UPI_ID = os.environ.get('UPI_ID') or 'yourname@okhdfcbank'
    UPI_NAME = os.environ.get('UPI_NAME') or 'Zone Business'
    
    # For SMS (optional - use Twilio)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Languages supported
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिन्दी',
        'mr': 'मराठी',
        'ta': 'தமிழ்'
    }
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional

class ContactForm(FlaskForm):
    """Contact form with validation"""
    name = StringField('Name', validators=[
        DataRequired(message='Please enter your name'),
        Length(min=2, max=50, message='Name must be between 2 and 50 characters')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(message='Please enter your email'),
        Email(message='Please enter a valid email address')
    ])
    
    phone = TelField('Phone Number', validators=[
        Optional(),
        Length(min=10, max=15, message='Please enter a valid phone number')
    ])
    
    message = TextAreaField('Message', validators=[
        DataRequired(message='Please enter your message'),
        Length(min=10, max=500, message='Message must be between 10 and 500 characters')
    ])
import datetime
import random

def get_current_time():
    """Returns current time in formatted string"""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

def get_random_orange_shade():
    """Generate random orange color shades"""
    orange_shades = [
        '#FF4500', '#FF8C00', '#FFA500', '#FF6347',
        '#FF7F50', '#FF8C69', '#FFA07A', '#FFB347',
        '#FF9933', '#FF8533'
    ]
    return random.choice(orange_shades)

def process_user_data(user_data):
    """Process user contact form data"""
    try:
        # Here you would typically save to database or send email
        print(f"Processing data for: {user_data['name']}")
        print(f"Message: {user_data['message']}")
        
        # Simulate successful processing
        return {
            'success': True,
            'message': 'Data processed successfully',
            'timestamp': datetime.datetime.now()
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'timestamp': datetime.datetime.now()
        }

def format_phone_number(phone):
    """Format phone number to readable format"""
    if phone and len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone
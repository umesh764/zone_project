from flask import Blueprint, session, request, redirect, url_for, flash

language_bp = Blueprint('language', __name__)

# Simple dictionary for translations
translations = {
    'en': {
        'home': 'Home',
        'about': 'About',
        'services': 'Services',
        'contact': 'Contact',
        'login': 'Login',
        'register': 'Register',
        'dashboard': 'Dashboard',
        'make_payment': 'Make Payment',
        'payment_history': 'Payment History',
        'logout': 'Logout',
        'welcome': 'Welcome to Zone',
        'enter_phone': 'Enter Mobile Number',
        'enter_password': 'Enter Password',
        'forgot_password': 'Forgot Password?',
        'scan_qr': 'Scan QR Code',
        'pay_now': 'Pay Now',
        'amount': 'Amount (₹)',
        'note': 'Note (Optional)',
        'transaction_id': 'Transaction ID',
        'status': 'Status',
        'date': 'Date',
        'download_receipt': 'Download Receipt'
    },
    'hi': {
        'home': 'होम',
        'about': 'हमारे बारे में',
        'services': 'सेवाएं',
        'contact': 'संपर्क',
        'login': 'लॉग इन',
        'register': 'रजिस्टर',
        'dashboard': 'डैशबोर्ड',
        'make_payment': 'भुगतान करें',
        'payment_history': 'भुगतान इतिहास',
        'logout': 'लॉग आउट',
        'welcome': 'ज़ोन में आपका स्वागत है',
        'enter_phone': 'मोबाइल नंबर दर्ज करें',
        'enter_password': 'पासवर्ड दर्ज करें',
        'forgot_password': 'पासवर्ड भूल गए?',
        'scan_qr': 'क्यूआर कोड स्कैन करें',
        'pay_now': 'अभी भुगतान करें',
        'amount': 'राशि (₹)',
        'note': 'नोट (वैकल्पिक)',
        'transaction_id': 'लेन-देन आईडी',
        'status': 'स्थिति',
        'date': 'तारीख',
        'download_receipt': 'रसीद डाउनलोड करें'
    },
    'mr': {
        'home': 'मुखपृष्ठ',
        'about': 'आमच्याबद्दल',
        'services': 'सेवा',
        'contact': 'संपर्क',
        'login': 'लॉगिन',
        'register': 'नोंदणी',
        'dashboard': 'डॅशबोर्ड',
        'make_payment': 'पेमेंट करा',
        'payment_history': 'पेमेंट इतिहास',
        'logout': 'लॉगआउट',
        'welcome': 'झोन मध्ये आपले स्वागत आहे',
        'enter_phone': 'मोबाइल नंबर टाका',
        'enter_password': 'पासवर्ड टाका',
        'forgot_password': 'पासवर्ड विसरलात?',
        'scan_qr': 'क्यूआर कोड स्कॅन करा',
        'pay_now': 'आता पेमेंट करा',
        'amount': 'रक्कम (₹)',
        'note': 'नोंद (वैकल्पिक)',
        'transaction_id': 'व्यवहार आयडी',
        'status': 'स्थिती',
        'date': 'तारीख',
        'download_receipt': 'पावती डाउनलोड करा'
    },
    'ta': {
        'home': 'முகப்பு',
        'about': 'எங்களைப் பற்றி',
        'services': 'சேவைகள்',
        'contact': 'தொடர்பு',
        'login': 'உள்நுழைய',
        'register': 'பதிவு',
        'dashboard': 'டாஷ்போர்டு',
        'make_payment': 'பணம் செலுத்து',
        'payment_history': 'பணம் செலுத்திய வரலாறு',
        'logout': 'வெளியேறு',
        'welcome': 'சோனுக்கு வரவேற்கிறோம்',
        'enter_phone': 'கைப்பேசி எண்ணை உள்ளிடவும்',
        'enter_password': 'கடவுச்சொல்லை உள்ளிடவும்',
        'forgot_password': 'கடவுச்சொல் மறந்துவிட்டதா?',
        'scan_qr': 'QR குறியீட்டை ஸ்கேன் செய்யவும்',
        'pay_now': 'இப்போது பணம் செலுத்து',
        'amount': 'தொகை (₹)',
        'note': 'குறிப்பு (விரும்பினால்)',
        'transaction_id': 'பரிவர்த்தனை ஐடி',
        'status': 'நிலை',
        'date': 'தேதி',
        'download_receipt': 'ரசீது பதிவிறக்கவும்'
    }
}

def get_text(key):
    """Get translated text based on session language"""
    lang = session.get('language', 'en')
    return translations.get(lang, translations['en']).get(key, key)

@language_bp.route('/language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['en', 'hi', 'mr', 'ta']:
        session['language'] = lang_code
        flash(f'Language changed', 'success')
    return redirect(request.referrer or url_for('auth.login'))
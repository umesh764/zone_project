from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
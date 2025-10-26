from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

L = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per hour"]
)

def rate_limit(limit_string):
    def decorator(fn):
        return L.limit(limit_string)(fn)
    return decorator
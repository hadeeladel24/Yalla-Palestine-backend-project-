
from functools import wraps
from flask import jsonify,Blueprint
from flask_jwt_extended import verify_jwt_in_request, get_jwt

role_required_routes=Blueprint('role_required',__name__)

@role_required_routes.route('/',methods=['GET'])
def home():
    return jsonify({"message":"Welcome to the role required API"}),200


def role_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify(msg="Access denied: insufficient permissions"), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
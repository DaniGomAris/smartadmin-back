from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

def role_required(allowed_roles: list):
    """
    Decorador para rutas protegidas por rol
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            role = identity.get("role", "user")
            if role not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 403
            return func(*args, role=role, **kwargs)
        return wrapper
    return decorator

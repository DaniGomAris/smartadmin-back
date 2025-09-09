from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def token_required(func):
    """
    Decorador que exige un JWT valido en la peticion
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"error": "Token inválido o ausente", "msg": str(e)}), 401
        return func(*args, **kwargs)
    return wrapper

def role_required(allowed_roles: list):
    """
    Decorador que exige un rol valido en el JWT
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            claims = get_jwt()
            role = claims.get("role", "user")

            if role not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 403

            return func(*args, user_id=user_id, role=role, **kwargs)
        return wrapper
    return decorator

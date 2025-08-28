from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

def role_required(allowed_roles):
    """
    Decorador que valida si el usuario tiene uno de los roles permitidos
    usando directamente el rol guardado en el JWT
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()

            user_id = identity.get("id")
            role = identity.get("role")

            if role not in allowed_roles:
                return jsonify({"error": "Unauthorized – Access denied"}), 403

            return fn(user_id=user_id, role=role, *args, **kwargs)
        return wrapper
    return decorator

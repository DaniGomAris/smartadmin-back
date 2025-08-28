from flask_jwt_extended import create_access_token

def generate_token(user_id: str, role: str) -> str:
    """
    Genera un JWT para un usuario con su ID y rol
    """
    return create_access_token(identity={"id": user_id, "role": role})

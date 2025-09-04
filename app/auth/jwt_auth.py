from flask_jwt_extended import create_access_token

def generate_token(user_id: str, role: str) -> str:
    """
    Genera un JWT para un usuario con su ID y rol
    """
    identity = str(user_id)
    additional_claims = {"role": role}
    
    return create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )

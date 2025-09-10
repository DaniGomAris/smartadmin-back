from flask_jwt_extended import create_access_token, decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
from datetime import datetime, timedelta

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

def generate_temporary_token(user_id: str, role: str, minutes: int = 10) -> str:
    """
    Genera un JWT temporal para un usuario con expiración corta (default: 5 minutos)
    """
    identity = str(user_id)
    additional_claims = {"role": role}

    expires = timedelta(minutes=minutes)

    return create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=expires
    )

def verify_token(token: str):
    """
    Verifica un JWT estándar o temporal y devuelve el payload si es válido.
    Devuelve None si el token está expirado o inválido.
    """
    try:
        decoded = decode_token(token)
        
        # Verifica expiración
        exp_timestamp = decoded.get("exp")
        if not exp_timestamp or datetime.utcnow().timestamp() > exp_timestamp:
            return None
        
        # Retorna la identidad
        return {
            "user_id": decoded.get("sub"),
            "role": decoded.get("role"),
            "exp": exp_timestamp
        }

    except JWTDecodeError:
        return None
    except Exception:
        return None
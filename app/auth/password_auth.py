from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configuracion
ph = PasswordHasher(
    time_cost=3,   
    memory_cost=64 * 1024,
    parallelism=2,   
    hash_len=32,    
    salt_len=16  
)

def hash_password(password: str) -> str:
    """
    Genera un hash Argon2 seguro para la contraseña
    """
    return ph.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifica si la contraseña ingresada coincide con el hash
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

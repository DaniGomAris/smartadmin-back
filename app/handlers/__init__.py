from .jwt_handlers import register_jwt_handlers
from .error_handlers import register_error_handlers

def register_all_handlers(app):
    """
    Registra todos los handlers de la aplicación
    """
    register_jwt_handlers(app)
    register_error_handlers(app)

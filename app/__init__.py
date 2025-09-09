from flask import Flask
from flask_cors import CORS
from .extensions import jwt
from .routes.user_route import user_bp
from .routes.auth_route import auth_bp
from .handlers import register_all_handlers
from .config.firebase import db
from .config.config import config_by_name
import os

def create_app():
    app = Flask(__name__)
    
    # Configuraciones de entorno
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env])
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    
    # Extensiones
    CORS(app)
    jwt.init_app(app)

    # Blueprints
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    # Handlers globales
    register_all_handlers(app)

    # Debugging de rutas registradas
    print("Rutas registradas:")
    for rule in app.url_map.iter_rules():   
        print(rule, rule.methods)
        
    return app

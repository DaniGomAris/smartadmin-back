from flask import Flask
from flask_cors import CORS
from .extensions import jwt, limiter
from .services.firebase import db
from .routes.user_route import user_bp
from config import config_by_name
import os

def create_app():
    app = Flask(__name__)
    
    # Carga la configuración desde config.py según ENV
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env])

    CORS(app)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(user_bp, url_prefix="/users")

    return app

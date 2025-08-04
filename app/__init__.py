from flask import Flask
from flask_cors import CORS
from .extensions import jwt, limiter
from .services.firebase import db
from .routes.user_route import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    CORS(app)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(user_bp, url_prefix="/users")
    return app

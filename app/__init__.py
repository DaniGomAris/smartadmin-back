from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import jwt, limiter
from .services.firebase import db
from .routes.user_route import user_bp
from config import config_by_name
import os

def create_app():
    app = Flask(__name__)
    
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name[env])

    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    CORS(app)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(user_bp, url_prefix="/users")

    @jwt.unauthorized_loader
    def unauthorized_response(err_str):
        return jsonify({"error": "Missing or invalid Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(err_str):
        return jsonify({"error": "Invalid token"}), 422

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has been revoked"}), 401

    print("📌 Rutas registradas:")
    for rule in app.url_map.iter_rules():   
        print(rule, rule.methods)
    return app

from flask import jsonify
from app.extensions import jwt

def register_jwt_handlers(app):
    """
    Registra los callbacks de JWT en la app de Flask.
    """
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

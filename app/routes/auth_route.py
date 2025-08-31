# auth_route.py
from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.extensions import limiter
from flask_limiter.util import get_remote_address

auth_bp = Blueprint("auth", __name__)
service = UserService()

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute", key_func=get_remote_address)
def login_user():
    data = request.get_json()
    document = data.get("document")
    password = data.get("password")
    response, status = service.login_user(document, password)
    return jsonify(response), status

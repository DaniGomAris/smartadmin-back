# auth_route.py
from flask import Blueprint, request, jsonify
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__)
service = UserService()

@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    document = data.get("document")
    password = data.get("password")
    response, status = service.login_user(document, password)
    return jsonify(response), status

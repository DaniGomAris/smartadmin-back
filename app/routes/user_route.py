from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.auth.decorators import role_required
from app.extensions import limiter

user_bp = Blueprint("users", __name__)
service = UserService()

@user_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin", "master"])
def get_users(user_id, role):
    return jsonify(service.get_users_by_role(role))

@user_bp.route("/all", methods=["GET"])
def get_all_users():
    return jsonify(service.get_all_users())

@user_bp.route("/", methods=["POST"])
@jwt_required()
def add_user():
    identity = get_jwt_identity()
    data = request.get_json()
    response, status = service.add_user(identity, data)
    return jsonify(response), status

@user_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin", "master"])
def delete_user(user_id, role, **kwargs):
    response, status = service.delete_user(role, user_id)
    return jsonify(response), status

@user_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    identity = get_jwt_identity()
    data = request.get_json()
    response, status = service.update_user(identity, user_id, data)
    return jsonify(response), status

@user_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute")
def login_user():
    data = request.get_json()
    response, status = service.login_user(data.get("email"), data.get("password"))
    return jsonify(response), status

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_logged_user():
    identity = get_jwt_identity()
    response, status = service.get_logged_user(identity.get("id"), identity.get("role"))
    return jsonify(response), status

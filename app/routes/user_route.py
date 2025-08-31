# user_route.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.auth.decorators import role_required

user_bp = Blueprint("users", __name__)
service = UserService()

# GET /users -> Obtener usuarios rol
@user_bp.route("/get-users", methods=["GET"])
@jwt_required()
@role_required(["admin", "master"])
def get_users():
    identity = get_jwt_identity()
    role = identity.get("role", "").lower()
    return jsonify(service.get_users(role))


# ----- QUITAR CUANDO SE TERMINEN LAS PRUEBAS -----
# GET /users -> Obtener todos los usuarios sin importar el rol
@user_bp.route("/all-users", methods=["GET"])
def get_all_users():
    return jsonify(service.get_all_users())


# ----- QUITAR CUANDO SE TERMINEN LAS PRUEBAS -----
# GET /users -> Obtener todos los usuarios sin importar el rol por consola
@user_bp.route("/all-users-console", methods=["GET"])
def get_all_users_console():
    return service.get_all_users_console()


# POST /users -> crear nuevo usuario
@user_bp.route("/create-user", methods=["POST"])
@jwt_required()
def add_user():
    identity = get_jwt_identity()
    data = request.get_json()
    response, status = service.add_user(identity, data)
    return jsonify(response), status


# PUT /users/<user_id> -> Actualizar usuario
@user_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    identity = get_jwt_identity()
    data = request.get_json()
    response, status = service.update_user(identity, user_id, data)
    return jsonify(response), status


# DELETE /users/<user_id> -> Eliminar usuario
@user_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin", "master"])
def delete_user(user_id):
    identity = get_jwt_identity()
    role = identity.get("role")
    response, status = service.delete_user(role, user_id)
    return jsonify(response), status

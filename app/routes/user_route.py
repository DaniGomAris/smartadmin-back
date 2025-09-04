# app/routes/user_route.py
from flask import Blueprint, jsonify, request
from app.services.user_service import UserService
from app.decorators.auth_decorators import token_required, role_required

user_bp = Blueprint("users", __name__)
service = UserService()

# GET /users -> Obtener usuarios según rol
@user_bp.route("/get-users", methods=["GET"])
@token_required
@role_required(["admin", "master"])
def get_users(user_id, role):
    """
    Retorna los usuarios visibles para el rol logueado.
    El rol y el id se obtienen del token JWT.
    """
    return jsonify(service.get_users(role))


# ----- SOLO PRUEBAS -----
@user_bp.route("/all-users", methods=["GET"])
def get_all_users():
    return jsonify(service.get_all_users())


@user_bp.route("/all-users-console", methods=["GET"])
def get_all_users_console():
    return service.get_all_users_console()


# POST /users -> crear nuevo usuario
@user_bp.route("/create-user", methods=["POST"])
@token_required
@role_required(["admin", "master"])
def add_user(user_id, role):
    """
    Crear nuevo usuario, validando permisos desde el rol en el token.
    """
    data = request.get_json()
    response, status = service.add_user(role, data)
    return jsonify(response), status


# PUT /users/<target_id> -> Actualizar usuario
@user_bp.route("/<target_id>", methods=["PUT"])
@token_required
@role_required(["admin", "master"])
def update_user(user_id, role, target_id):
    """
    Actualizar usuario objetivo (target_id),
    validando permisos con rol e id del token.
    """
    data = request.get_json()
    response, status = service.update_user({"role": role, "id": user_id}, target_id, data)
    return jsonify(response), status


# DELETE /users/<target_id> -> Eliminar usuario
@user_bp.route("/<target_id>", methods=["DELETE"])
@token_required
@role_required(["admin", "master"])
def delete_user(user_id, role, target_id):
    """
    Eliminar usuario objetivo (target_id),
    validando permisos con rol e id del token.
    """
    response, status = service.delete_user({"role": role, "id": user_id}, target_id)
    return jsonify(response), status

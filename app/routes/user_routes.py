from flask import Blueprint
from app.controllers.user_controller import UserController
from app.decorators.auth_decorators import token_required, role_required

user_bp = Blueprint("users", __name__)

# ----- SOLO PRUEBAS -----
user_bp.route("/all-users", methods=["GET"])(UserController.get_all_users)
user_bp.route("/all-users-console", methods=["GET"])(UserController.get_all_users_console)

# GET /users -> Obtener usuarios segun rol
user_bp.route("/", methods=["GET"])(
    token_required(role_required(["admin", "master"])(UserController.get_users))
)

# POST /users -> Crear nuevo usuario
user_bp.route("/", methods=["POST"])(
    token_required(role_required(["admin", "master"])(UserController.add_user))
)

# PUT /users/<target_id> -> Actualizar usuario
user_bp.route("/<target_id>", methods=["PUT"])(
    token_required(role_required(["admin", "master"])(UserController.update_user))
)

# DELETE /users/<target_id> -> Eliminar usuario
user_bp.route("/<target_id>", methods=["DELETE"])(
    token_required(role_required(["admin", "master"])(UserController.delete_user))
)

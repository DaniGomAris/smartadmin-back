from flask import Blueprint
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)
auth_bp.route("/login", methods=["POST"])(AuthController.login_user)

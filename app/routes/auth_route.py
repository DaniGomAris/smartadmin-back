import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.auth.password_handler import verify_password
from app.auth.jwt_handler import generate_token
from app.utils.response_handler import success_response, error_response
from app.extensions import limiter

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

# ---------------------------
# Login
# ---------------------------
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute")
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user_doc = UserService.get_user_by_email(email)
    if user_doc is None:
        return error_response({"email": "User not found"}, status_code=404)

    user_data = user_doc.to_dict()
    if not verify_password(user_data.get("password", ""), password):
        return error_response({"password": "Invalid password"}, status_code=401)

    role = user_data.get("role", "user")
    access_token = generate_token(user_doc.id, role)

    user_data.pop("password", None)
    logger.info(f"User logged in: {user_doc.id}")

    return success_response({
        "access_token": access_token,
        "user": {**user_data, "id": user_doc.id, "role": role}
    })

import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from app.services.firebase import db
from app.extensions import limiter
from app.utils.user_validator import UserValidator
from app.auth.decorators import admin_required

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_bp = Blueprint("users", __name__)
validator = UserValidator(db)

def extract_fields(data, *fields):
    return tuple(data.get(field) for field in fields)


# ---------------------------
# Get all users (admin only)
# ---------------------------
@user_bp.route("/", methods=["GET"])
#@jwt_required()
#@admin_required
def get_users():
    try:
        users = []
        for doc in db.collection("users").stream():
            user_data = doc.to_dict()
            user_data.pop("password", None)
            user_data["id"] = doc.id
            users.append(user_data)
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error in get_users: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Register new user
# ---------------------------
@user_bp.route("/", methods=["POST"])
def add_user():
    data = request.get_json()
    document, document_type, role, name, last_name1, last_name2, email, phone, password, re_password = extract_fields(
        data, "document", "document_type", "role", "name", "last_name1", "last_name2", "email", "phone", "password", "re_password"
    )

    format_errors = {}

    if not validator.is_valid_document(document):
        format_errors["document"] = "Invalid document format"
    if not validator.is_valid_document_type(document_type):
        format_errors["document_type"] = "Invalid document type"
    if not validator.is_valid_role(role):
        format_errors["role"] = "Invalid role format"
    if not validator.is_valid_name(name):
        format_errors["name"] = "Invalid name format"
    if not validator.is_valid_last_name(last_name1) or not validator.is_valid_last_name(last_name2):
        format_errors["last_names"] = "Invalid last names format"
    if not validator.is_valid_email(email):
        format_errors["email"] = "Invalid email format"
    if not validator.is_valid_phone(phone):
        format_errors["phone"] = "Invalid phone format"
    if not validator.is_valid_password(password):
        format_errors["password"] = "Invalid password format"
    if not validator.is_valid_re_password(password, re_password):
        format_errors["re_password"] = "Passwords do not match"

    if format_errors:
        return jsonify({"error": format_errors}), 400

    conflict_errors = {}

    if validator.is_document_registered(document):
        conflict_errors["document"] = "Document already registered"
    if validator.is_email_registered(email):
        conflict_errors["email"] = "Email already registered"

    if conflict_errors:
        return jsonify({"error": conflict_errors}), 409

    try:
        document_id = str(document)
        data["role"] = role
        data["password"] = generate_password_hash(password)
        data.pop("re_password", None)
        data.pop("document", None)
        db.collection("users").document(document_id).set(data)

        logger.info(f"New user registered: {document}")
        return jsonify({"message": "User added", "id": document}), 201
    except Exception as e:
        logger.error(f"Error in add_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Delete user (admin only)
# ---------------------------
@user_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    try:
        db.collection("users").document(user_id).delete()
        logger.info(f"User deleted: {user_id}")
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        logger.error(f"Error in delete_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Update user (protected)
# ---------------------------
@user_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    try:
        db.collection("users").document(user_id).update(data)
        logger.info(f"User updated: {user_id}")
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        logger.error(f"Error in update_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Login and generate JWT token
# ---------------------------
@user_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute")
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        users = db.collection("users").where("email", "==", email).stream()
        user = next(users, None)

        if user is None:
            return jsonify({"error": "User not found"}), 404

        user_data = user.to_dict()
        if not check_password_hash(user_data.get("password", ""), password):
            return jsonify({"error": "Invalid password"}), 401

        access_token = create_access_token(identity=user.id)
        user_data.pop("password", None)
        logger.info(f"User logged in: {user.id}")

        return jsonify({
            "access_token": access_token,
            "user": {**user_data, "id": user.id}
        }), 200

    except Exception as e:
        logger.error(f"Error in login_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Get logged-in user info
# ---------------------------
@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_logged_user():
    user_id = get_jwt_identity()
    try:
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        user_data.pop("password", None)
        return jsonify({**user_data, "id": user_doc.id}), 200
    except Exception as e:
        logger.error(f"Error in get_logged_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

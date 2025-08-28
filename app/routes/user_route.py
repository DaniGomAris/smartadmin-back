import logging
import json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.auth.password_handler import hash_password, verify_password
from app.services.firebase import db
from app.extensions import limiter
from app.utils.user_validator import UserValidator
from app.auth.decorators import role_required

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint
user_bp = Blueprint("users", __name__)
validator = UserValidator(db)


# ---------------------------
# Helpers
# ---------------------------
def extract_fields(data, *fields):
    """Extrae campos de un diccionario en el orden indicado"""
    return tuple(data.get(field) for field in fields)


def format_user(doc):
    """Devuelve datos de usuario sin la contraseña"""
    data = doc.to_dict()
    data.pop("password", None)
    data["id"] = doc.id
    return data


def validate_user_data(data, check_password=True):
    """Valida datos básicos del usuario y devuelve errores"""
    document, document_type, role, name, last_name1, last_name2, email, phone, password, re_password = extract_fields(
        data, "document", "document_type", "role", "name", "last_name1", "last_name2",
        "email", "phone", "password", "re_password"
    )

    errors = {}
    if not validator.is_valid_document(document):
        errors["document"] = "Invalid document format"
    if not validator.is_valid_document_type(document_type):
        errors["document_type"] = "Invalid document type"
    if not validator.is_valid_name(name):
        errors["name"] = "Invalid name format"
    if not validator.is_valid_last_name(last_name1) or not validator.is_valid_last_name(last_name2):
        errors["last_names"] = "Invalid last names format"
    if not validator.is_valid_email(email):
        errors["email"] = "Invalid email format"
    if not validator.is_valid_phone(phone):
        errors["phone"] = "Invalid phone format"

    if check_password:
        if not validator.is_valid_password(password):
            errors["password"] = "Invalid password format"
        if not validator.is_valid_re_password(password, re_password):
            errors["re_password"] = "Passwords do not match"

    return errors


# ---------------------------
# Get all users (restricted by role)
# ---------------------------
@user_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin", "master"])
def get_users(user_id, role):
    try:
        users = []
        for doc in db.collection("users").stream():
            user_data = doc.to_dict()
            target_role = user_data.get("role")

            if role == "master" and target_role in ["admin", "user"]:
                users.append(format_user(doc))
            elif role == "admin" and target_role == "user":
                users.append(format_user(doc))

        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error in get_users: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Metodo de prueba (todos los usuarios sin restricciones)
# ---------------------------
@user_bp.route("/all", methods=["GET"])
def get_all_users():
    try:
        users = [format_user(doc) for doc in db.collection("users").stream()]
        return Response(
            json.dumps(users, indent=4, ensure_ascii=False),
            mimetype="application/json"
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# Register new user (Argon2 + restricted roles)
# ---------------------------
@user_bp.route("/", methods=["POST"])
@jwt_required()
def add_user():
    identity = get_jwt_identity()
    current_role = identity.get("role")
    data = request.get_json()

    # Validaciones
    format_errors = validate_user_data(data)
    if format_errors:
        return jsonify({"error": format_errors}), 400

    conflict_errors = {}
    if validator.is_document_registered(data["document"]):
        conflict_errors["document"] = "Document already registered"
    if validator.is_email_registered(data["email"]):
        conflict_errors["email"] = "Email already registered"
    if conflict_errors:
        return jsonify({"error": conflict_errors}), 409

    # Restricciones de rol
    if current_role == "master" and data["role"] not in ["admin", "user"]:
        return jsonify({"error": "Master can only assign roles 'admin' or 'user'"}), 403
    if current_role == "admin" and data["role"] != "user":
        return jsonify({"error": "Admin can only create users with role 'user'"}), 403

    try:
        user_doc = {
            "document_type": data["document_type"],
            "role": data["role"],
            "name": data["name"],
            "last_name1": data["last_name1"],
            "last_name2": data["last_name2"],
            "email": data["email"],
            "phone": data["phone"],
            "password": hash_password(data["password"]),  # Argon2
        }

        db.collection("users").document(str(data["document"])).set(user_doc)
        logger.info(f"New user registered: {data['document']} by {identity['id']}")
        return jsonify({"message": "User added", "id": data["document"]}), 201
    except Exception as e:
        logger.error(f"Error in add_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Delete user
# ---------------------------
@user_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin", "master"])
def delete_user(user_id, role, **kwargs):
    try:
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        target_role = user_doc.to_dict().get("role")
        if role == "admin" and target_role != "user":
            return jsonify({"error": "Admin can only delete users"}), 403
        if role == "master" and target_role not in ["admin", "user"]:
            return jsonify({"error": "Master can only delete admins or users"}), 403

        db.collection("users").document(user_id).delete()
        logger.info(f"User deleted: {user_id}")
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        logger.error(f"Error in delete_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Update user
# ---------------------------
@user_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    identity = get_jwt_identity()
    current_role = identity.get("role")

    try:
        target_doc = db.collection("users").document(user_id).get()
        if not target_doc.exists:
            return jsonify({"error": "Target user not found"}), 404

        target_role = target_doc.to_dict().get("role", "user")

        # Restricciones
        if current_role == "user":
            return jsonify({"error": "Users cannot update other users"}), 403
        if current_role == "admin" and target_role != "user":
            return jsonify({"error": "Admins can only update users"}), 403

        data = request.get_json()
        update_data = {}

        if "name" in data and validator.is_valid_name(data["name"]):
            update_data["name"] = data["name"]
        if "last_name1" in data and validator.is_valid_last_name(data["last_name1"]):
            update_data["last_name1"] = data["last_name1"]
        if "last_name2" in data and validator.is_valid_last_name(data["last_name2"]):
            update_data["last_name2"] = data["last_name2"]
        if "phone" in data and validator.is_valid_phone(data["phone"]):
            update_data["phone"] = data["phone"]
        if "email" in data and validator.is_valid_email(data["email"]):
            update_data["email"] = data["email"]

        # Cambio de rol → solo master
        if "role" in data:
            if current_role != "master":
                return jsonify({"error": "Only master can modify roles"}), 403
            if data["role"] not in ["admin", "user"]:
                return jsonify({"error": "Invalid role"}), 400
            update_data["role"] = data["role"]

        # Cambio de contraseña
        if "password" in data:
            if not validator.is_valid_password(data["password"]):
                return jsonify({"error": "Invalid password format"}), 400
            update_data["password"] = hash_password(data["password"])

        if update_data:
            db.collection("users").document(user_id).update(update_data)
            logger.info(f"User {user_id} updated by {identity['id']}")
            return jsonify({"message": "User updated"}), 200

        return jsonify({"error": "No valid fields to update"}), 400
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------
# Login (Argon2 verify)
# ---------------------------
@user_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute")
def login_user():
    data = request.get_json()
    email, password = data.get("email"), data.get("password")

    try:
        users = db.collection("users").where("email", "==", email).stream()
        user = next(users, None)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = user.to_dict()
        if not verify_password(user_data.get("password", ""), password):
            return jsonify({"error": "Invalid password"}), 401

        role = user_data.get("role", "user")
        access_token = create_access_token(identity={"id": user.id, "role": role})

        return jsonify({
            "access_token": access_token,
            "user": {**format_user(user), "role": role}
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
    identity = get_jwt_identity()
    user_id = identity.get("id")

    try:
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = format_user(user_doc)
        return jsonify({
            "id": user_doc.id,
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "role": identity.get("role", "user")
        }), 200
    except Exception as e:
        logger.error(f"Error in get_logged_user: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

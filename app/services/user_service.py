import logging
import json
from flask import Response

from app.auth.jwt_handler import generate_token
from app.auth.password_handler import hash_password, verify_password
from app.services.firebase import db
from app.validators.user_validator import UserValidator
from app.utils.permission_utils import (
    can_delete_user,
    can_update_user,
    can_assign_role,
)

logger = logging.getLogger(__name__)
validator = UserValidator(db)


class UserService:
    """
    Servicio que maneja la lógica de negocio relacionada con los usuarios.
    Incluye operaciones CRUD, login y validaciones.
    """

    # ==============================
    # GET USERS
    # ==============================
    @staticmethod
    def get_users(current_role: str):
        """
        Retorna los usuarios visibles según el rol del usuario logueado.
        - master -> puede ver admins
        - admin  -> puede ver users
        """
        users = []
        for doc in db.collection("users").stream():
            user_data = doc.to_dict()
            user_role = user_data.get("role", "").lower()

            if current_role == "master" and user_role == "admin":
                user_data.pop("password", None)
                user_data["id"] = doc.id
                users.append(user_data)
            elif current_role == "admin" and user_role == "user":
                user_data.pop("password", None)
                user_data["id"] = doc.id
                users.append(user_data)
        return users

    # ----- MÉTODOS DE PRUEBA (QUITAR EN PRODUCCIÓN) -----
    @staticmethod
    def get_all_users():
        """
        Retorna TODOS los usuarios sin filtrar roles (SOLO PARA PRUEBAS).
        """
        users = []
        for doc in db.collection("users").stream():
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            users.append(user_data)
        return users

    @staticmethod
    def get_all_users_console():
        """
        Retorna TODOS los usuarios con indentación en consola (SOLO PARA PRUEBAS).
        """
        users = []
        for doc in db.collection("users").stream():
            data = doc.to_dict()
            ordered_data = {
                doc.id: {
                    "name": data.get("name"),
                    "last_name1": data.get("last_name1"),
                    "last_name2": data.get("last_name2"),
                    "password": data.get("password"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    "role": data.get("role"),
                }
            }
            users.append(ordered_data)
        return Response(json.dumps(users, indent=4), mimetype="application/json")

    # ==============================
    # ADD USER
    # ==============================
    @staticmethod
    def add_user(current_role: str, data: dict):
        """
        Registra un nuevo usuario validando permisos, formato y duplicados.
        """
        document = data.get("document")
        document_type = data.get("document_type")
        role = data.get("role")
        name = data.get("name")
        last_name1 = data.get("last_name1")
        last_name2 = data.get("last_name2")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        re_password = data.get("re_password")

        # Validaciones de formato
        format_errors = {}
        if not validator.is_valid_document(document):
            format_errors["document"] = "Invalid document format"
        if not validator.is_valid_document_type(document_type):
            format_errors["document_type"] = "Invalid document type"
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
            return {"error": format_errors}, 400

        conflict_errors = {}
        if validator.is_document_registered(document):
            conflict_errors["document"] = "Document already registered"
        if validator.is_email_registered(email):
            conflict_errors["email"] = "Email already registered"
        if conflict_errors:
            return {"error": conflict_errors}, 409

        if not can_assign_role(current_role, role):
            return {"error": "You cannot assign this role"}, 403

        try:
            new_user = {
                "document_type": document_type,
                "role": role,
                "name": name,
                "last_name1": last_name1,
                "last_name2": last_name2,
                "email": email,
                "phone": phone,
                "password": hash_password(password),
            }
            db.collection("users").document(str(document)).set(new_user)
            logger.info(f"New user registered: {document} by role {current_role}")
            return {"message": "User added", "id": document}, 201
        except Exception as e:
            logger.error(f"Error in add_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # UPDATE USER
    # ==============================
    @staticmethod
    def update_user(identity: dict, user_id: str, data: dict):
        """
        Actualiza datos de un usuario validando permisos y formato.
        """
        current_role = identity.get("role")
        current_id = identity.get("id")

        try:
            target_doc = db.collection("users").document(user_id).get()
            if not target_doc.exists:
                return {"error": "Target user not found"}, 404

            target_role = target_doc.to_dict().get("role", "user")
            if not can_update_user(current_role, target_role):
                return {"error": "You do not have permission to update this user"}, 403

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

            if "role" in data:
                if current_role != "master":
                    return {"error": "Only master can modify roles"}, 403
                if not can_assign_role("master", data["role"]):
                    return {"error": "Invalid role"}, 400
                update_data["role"] = data["role"]

            if "password" in data:
                if not validator.is_valid_password(data["password"]):
                    return {"error": "Invalid password format"}, 400
                update_data["password"] = hash_password(data["password"])

            if update_data:
                db.collection("users").document(user_id).update(update_data)
                logger.info(f"User {user_id} updated by {current_id}")
                return {"message": "User updated"}, 200

            return {"error": "No valid fields to update"}, 400
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # DELETE USER
    # ==============================
    @staticmethod
    def delete_user(identity: dict, user_id: str):
        """
        Elimina un usuario validando permisos.
        """
        current_role = identity.get("role")

        try:
            target_doc = db.collection("users").document(user_id).get()
            if not target_doc.exists:
                return {"error": "User not found"}, 404

            target_role = target_doc.to_dict().get("role", "user")
            if not can_delete_user(current_role, target_role):
                return {"error": "You do not have permission to delete this user"}, 403

            db.collection("users").document(user_id).delete()
            logger.info(f"User deleted: {user_id}")
            return {"message": "User deleted"}, 200
        except Exception as e:
            logger.error(f"Error in delete_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # LOGIN
    # ==============================
    @staticmethod
    def login_user(document: str, password: str):
        """
        Login de usuario validando documento y contraseña.
        Retorna JWT.
        """
        try:
            user_doc = db.collection("users").document(document).get()
            if not user_doc.exists:
                return {"error": "Documento o contraseña incorrectos"}, 404

            user_data = user_doc.to_dict()
            if not verify_password(user_data.get("password", ""), password):
                return {"error": "Documento o contraseña incorrectos"}, 401

            role = user_data.get("role", "user")
            access_token = generate_token(document, role)

            logger.info(f"User logged in: {document} with role {role}")
            return {
                "message": "Login exitoso",
                "access_token": access_token,
                "user": {"id": document, "role": role},
            }, 200
        except Exception as e:
            logger.error(f"Error in login_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # GET LOGGED USER
    # ==============================
    @staticmethod
    def get_logged_user(user_id: str, role: str):
        """
        Retorna información básica del usuario logueado.
        """
        try:
            user_doc = db.collection("users").document(user_id).get()
            if not user_doc.exists:
                return {"error": "User not found"}, 404

            return {"id": user_doc.id, "role": role}, 200
        except Exception as e:
            logger.error(f"Error in get_logged_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

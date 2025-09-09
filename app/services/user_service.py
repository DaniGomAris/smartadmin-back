# smartadmin-back/app/services/user_service.py

import logging
import json
from flask import Response
from bson.objectid import ObjectId

from app.auth.jwt_auth import generate_token
from app.auth.password_auth import hash_password, verify_password
from app.config.mongo_config import db
from app.validators.user_validator import UserValidator
from app.utils.permission_utils import (
    can_delete_user,
    can_update_user,
    can_assign_role,
)

logger = logging.getLogger(__name__)
validator = UserValidator(db["users"])
users_collection = db["users"]


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
        users = []
        try:
            for user_data in users_collection.find({}):
                user_role = user_data.get("role", "").lower()

                if current_role == "master" and user_role == "admin":
                    user_data.pop("password", None)
                    user_data["id"] = str(user_data["_id"])
                    users.append(user_data)
                elif current_role == "admin" and user_role == "user":
                    user_data.pop("password", None)
                    user_data["id"] = str(user_data["_id"])
                    users.append(user_data)
            return users
        except Exception as e:
            logger.error(f"Error in get_users: {e}", exc_info=True)
            return []

    # ----- MÉTODOS DE PRUEBA -----
    @staticmethod
    def get_all_users():
        users = []
        for user_data in users_collection.find({}):
            user_data["id"] = str(user_data["_id"])
            user_data.pop("password", None)
            users.append(user_data)
        return users

    @staticmethod
    def get_all_users_console():
        users = []
        for user_data in users_collection.find({}):
            ordered_data = {
                str(user_data["_id"]): {
                    "name": user_data.get("name"),
                    "last_name1": user_data.get("last_name1"),
                    "last_name2": user_data.get("last_name2"),
                    "password": user_data.get("password"),
                    "email": user_data.get("email"),
                    "phone": user_data.get("phone"),
                    "role": user_data.get("role"),
                }
            }
            users.append(ordered_data)
        return Response(json.dumps(users, indent=4), mimetype="application/json")

    # ==============================
    # ADD USER
    # ==============================
    @staticmethod
    def add_user(current_role: str, data: dict):
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
                "_id": str(document),  # documento como clave primaria
                "document_type": document_type,
                "role": role,
                "name": name,
                "last_name1": last_name1,
                "last_name2": last_name2,
                "email": email,
                "phone": phone,
                "password": hash_password(password),
            }
            users_collection.insert_one(new_user)
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
        current_role = identity.get("role")
        current_id = identity.get("id")

        try:
            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "Target user not found"}, 404

            target_role = target_doc.get("role", "user")
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
                users_collection.update_one({"_id": str(user_id)}, {"$set": update_data})
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
        current_role = identity.get("role")

        try:
            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "User not found"}, 404

            target_role = target_doc.get("role", "user")
            if not can_delete_user(current_role, target_role):
                return {"error": "You do not have permission to delete this user"}, 403

            users_collection.delete_one({"_id": str(user_id)})
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
        try:
            user_doc = users_collection.find_one({"_id": str(document)})
            if not user_doc:
                return {"error": "Documento o contraseña incorrectos"}, 404

            if not verify_password(user_doc.get("password", ""), password):
                return {"error": "Documento o contraseña incorrectos"}, 401

            role = user_doc.get("role", "user")
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
        try:
            user_doc = users_collection.find_one({"_id": str(user_id)})
            if not user_doc:
                return {"error": "User not found"}, 404

            return {"id": str(user_doc["_id"]), "role": role}, 200
        except Exception as e:
            logger.error(f"Error in get_logged_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

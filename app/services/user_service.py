import logging
import json
from flask import Response

from app.auth.jwt_auth import generate_token
from app.auth.password_auth import hash_password, verify_password
from app.config.mongo_config import db
from app.models.user import User
from app.validators.user_validator import UserValidator
from app.utils.permission_utils import (
    can_delete_user,
    can_update_user,
    can_assign_role,
)

logger = logging.getLogger(__name__)
users_collection = db["users"]
validator = UserValidator(users_collection)


class UserService:


    # ---------------------------
    # Obtener usuarios segun rol
    # ---------------------------
    @staticmethod
    def get_users(current_role: str):
        users = []
        try:
            for doc in users_collection.find({}):
                user_role = doc.get("role", "").lower()

                if (current_role == "master" and user_role == "admin") or \
                   (current_role == "admin" and user_role == "user"):
                    user = UserService._doc_to_user(doc, hide_password=True)
                    users.append(user.to_dict())
            return users
        except Exception as e:
            logger.error(f"Error in get_users: {e}", exc_info=True)
            return []

    @staticmethod
    def get_all_users():
        return [
            UserService._doc_to_user(doc, hide_password=True).to_dict()
            for doc in users_collection.find({})
        ]

    # ---------------------------
    # Añadir usuario
    # ---------------------------
    @staticmethod
    def add_user(current_role: str, data: dict):
        document = data.get("document")
        password = data.get("password")
        re_password = data.get("re_password")

        # Validaciones
        format_errors = {}
        if not validator.is_valid_document(document):
            format_errors["document"] = "Invalid document format"
        if not validator.is_valid_document_type(data.get("document_type")):
            format_errors["document_type"] = "Invalid document type"
        if not validator.is_valid_name(data.get("name")):
            format_errors["name"] = "Invalid name format"
        if not validator.is_valid_last_name(data.get("last_name1")) or \
           not validator.is_valid_last_name(data.get("last_name2")):
            format_errors["last_names"] = "Invalid last names format"
        if not validator.is_valid_email(data.get("email")):
            format_errors["email"] = "Invalid email format"
        if not validator.is_valid_phone(data.get("phone")):
            format_errors["phone"] = "Invalid phone format"
        if not validator.is_valid_password(password):
            format_errors["password"] = "Invalid password format"
        if not validator.is_valid_re_password(password, re_password):
            format_errors["re_password"] = "Passwords do not match"

        if format_errors:
            return {"error": format_errors}, 400

        # Conflictos
        if validator.is_document_registered(document):
            return {"error": {"document": "Document already registered"}}, 409
        if validator.is_email_registered(data.get("email")):
            return {"error": {"email": "Email already registered"}}, 409

        if not can_assign_role(current_role, data.get("role")):
            return {"error": "You cannot assign this role"}, 403

        try:
            new_user = User(
                id=str(document),
                document_type=data.get("document_type"),
                role=data.get("role"),
                name=data.get("name"),
                last_name1=data.get("last_name1"),
                last_name2=data.get("last_name2"),
                email=data.get("email"),
                phone=data.get("phone"),
                password=hash_password(password),
            )
            users_collection.insert_one(new_user.to_dict())
            logger.info(f"New user registered: {document} by role {current_role}")
            return {"message": "User added", "id": document}, 201
        except Exception as e:
            logger.error(f"Error in add_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500


    # ---------------------------
    # Añadir usuario
    # ---------------------------
    @staticmethod
    def add_user(current_role: str, data: dict):
        document = data.get("document")
        password = data.get("password")
        re_password = data.get("re_password")

        # Validaciones
        format_errors = {}
        if not validator.is_valid_document(document):
            format_errors["document"] = "Invalid document format"
        if not validator.is_valid_document_type(data.get("document_type")):
            format_errors["document_type"] = "Invalid document type"
        if not validator.is_valid_name(data.get("name")):
            format_errors["name"] = "Invalid name format"
        if not validator.is_valid_last_name(data.get("last_name1")) or \
        not validator.is_valid_last_name(data.get("last_name2")):
            format_errors["last_names"] = "Invalid last names format"
        if not validator.is_valid_email(data.get("email")):
            format_errors["email"] = "Invalid email format"
        if not validator.is_valid_phone(data.get("phone")):
            format_errors["phone"] = "Invalid phone format"
        if not validator.is_valid_password(password):
            format_errors["password"] = "Invalid password format"
        if not validator.is_valid_re_password(password, re_password):
            format_errors["re_password"] = "Passwords do not match"

        if format_errors:
            return {"error": format_errors}, 400

        # Conflictos
        if validator.is_document_registered(document):
            return {"error": {"document": "Document already registered"}}, 409
        if validator.is_email_registered(data.get("email")):
            return {"error": {"email": "Email already registered"}}, 409

        if not can_assign_role(current_role, data.get("role")):
            return {"error": "You cannot assign this role"}, 403

        try:
            new_user = User(
                id=str(document),
                document_type=data.get("document_type"),
                role=data.get("role"),
                name=data.get("name"),
                last_name1=data.get("last_name1"),
                last_name2=data.get("last_name2"),
                email=data.get("email"),
                phone=data.get("phone"),
                password=hash_password(password),
            )
            users_collection.insert_one(new_user.to_dict())
            logger.info(f"New user registered: {document} by role {current_role}")
            return {"message": "User added", "id": document}, 201
        except Exception as e:
            logger.error(f"Error in add_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500


    # ---------------------------
    # Actualizar usuario
    # ---------------------------
    @staticmethod
    def update_user(identity: dict, user_id: str, data: dict):
        current_role = identity.get("role")

        try:
            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "Target user not found"}, 404

            target_role = target_doc.get("role", "user")
            if not can_update_user(current_role, target_role):
                return {"error": "You do not have permission"}, 403

            update_data = {}
            if "name" in data and validator.is_valid_name(data["name"]):
                update_data["name"] = data["name"]
            if "last_name1" in data and validator.is_valid_last_name(data["last_name1"]):
                update_data["last_name1"] = data["last_name1"]
            if "last_name2" in data and validator.is_valid_last_name(data["last_name2"]):
                update_data["last_name2"] = data["last_name2"]
            if "phone" in data and validator.is_valid_phone(data["phone"]):
                update_data["phone"] = data["phone"]

            if "email" in data:
                if not validator.is_valid_email(data["email"]):
                    return {"error": "Invalid email format"}, 400
                # Valida si ya existe, pero permite mantener el mismo correo
                if validator.is_email_registered(data["email"]) and data["email"] != target_doc.get("email"):
                    return {"error": {"email": "Email already registered"}}, 409
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
                logger.info(f"User {user_id} updated by {identity.get('id')}")
                return {"message": "User updated"}, 200

            return {"error": "No valid fields to update"}, 400
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ---------------------------
    # Eliminar usuario
    # ---------------------------
    @staticmethod
    def delete_user(identity: dict, user_id: str):
        """
        Permite eliminar un usuario si el rol actual tiene permisos sobre el rol del usuario objetivo.
        """
        current_role = identity.get("role")
        try:
            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "Target user not found"}, 404

            target_role = target_doc.get("role", "user")
            if not can_delete_user(current_role, target_role):
                return {"error": "You do not have permission to delete this user"}, 403

            users_collection.delete_one({"_id": str(user_id)})
            logger.info(f"User {user_id} deleted by {identity.get('id')}")
            return {"message": "User deleted"}, 200
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ---------------------------
    # Iniciar sesion
    # ---------------------------
    @staticmethod
    def login_user(document: str, password: str):
        try:
            user_doc = users_collection.find_one({"_id": str(document)})
            if not user_doc:
                return {"error": "Documento incorrectos"}, 404

            if not verify_password(user_doc.get("password", ""), password):
                return {"error": "Contraseña incorrecta"}, 401

            role = user_doc.get("role", "user")
            token = generate_token(document, role)

            logger.info(f"User logged in: {document} with role {role}")
            return {
                "message": "Login exitoso",
                "access_token": token,
                "user": {"id": document, "role": role},
            }, 200
        except Exception as e:
            logger.error(f"Error in login_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500


    # ---------------------------
    # Obtener usuario logueado
    # ---------------------------
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


    # ---------------------------
    # Documento MongoDB a objetos User
    # ---------------------------
    @staticmethod
    def _doc_to_user(doc: dict, hide_password: bool = False) -> User:
        """Convierte un documento Mongo en un objeto User"""
        if hide_password:
            doc.pop("password", None)
        return User(
            id=str(doc["_id"]),
            document_type=doc.get("document_type", ""),
            role=doc.get("role", "user"),
            name=doc.get("name", ""),
            last_name1=doc.get("last_name1", ""),
            last_name2=doc.get("last_name2", ""),
            email=doc.get("email", ""),
            phone=doc.get("phone", ""),
            password=doc.get("password"),
        )

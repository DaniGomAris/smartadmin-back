import logging

from app.auth.jwt_auth import generate_token
from flask_jwt_extended import get_jwt_identity, get_jwt, create_access_token
from app.auth.password_auth import hash_password, verify_password
from app.config.mongo_config import db
from app.validators.user_validator import UserValidator
from app.utils.permission_utils import RolePermissions

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
    def get_users():
        """
        Devuelve usuarios según el rol extraído del JWT.
        """


        users = []
        try:
            claims = get_jwt()
            current_role = claims.get("role", "user")

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

    # ----- METODOS DE PRUEBA -----
    @staticmethod
    def get_all_users():
        users = []
        for user_data in users_collection.find({}):
            user_data["id"] = str(user_data["_id"])
            users.append(user_data)
        return users


    # ==============================
    # ADD USER
    # ==============================
    @staticmethod
    def add_user(data: dict):
        """
        Crea un nuevo usuario. Extrae el rol del usuario logueado desde el JWT
        y valida que pueda asignar el rol indicado al nuevo usuario.
        """
        try:
            current_id = get_jwt_identity()
            claims = get_jwt()
            current_role = claims.get("role", "user")
        except Exception as e:
            logger.error(f"Error extracting JWT info: {e}", exc_info=True)
            return {"error": "Invalid token"}, 401

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

        # Conflictos
        conflict_errors = {}
        if validator.is_document_registered(document):
            conflict_errors["document"] = "Document already registered"
        if validator.is_email_registered(email):
            conflict_errors["email"] = "Email already registered"
        if conflict_errors:
            return {"error": conflict_errors}, 409

        # Validación de rol según usuario logueado
        if not RolePermissions.can_create_user(current_role, role):
            return {"error": "You cannot create a user with this role"}, 403

        try:
            new_user = {
                "_id": str(document),
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
            logger.info(f"New user registered: {document} by {current_role} ({current_id})")
            return {"message": "User added", "id": document}, 201
        except Exception as e:
            logger.error(f"Error in add_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # UPDATE USER
    # ==============================
    @staticmethod
    def update_user(user_id: str, data: dict):
        """
        Actualiza un usuario. Extrae role y id del JWT para mayor seguridad.
        """
        try:
            current_id = get_jwt_identity()
            claims = get_jwt()
            current_role = claims.get("role", "user")

            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "Target user not found"}, 404

            target_role = target_doc.get("role", "user")
            if not RolePermissions.can_update_user(current_role, target_role):
                return {"error": "You do not have permission to update this user"}, 403

            allowed_fields = ["name", "last_name1", "last_name2", "phone", "email", "password", "role"]
            update_data = {}
            for field in allowed_fields:
                if field in data:
                    if field in ["name", "last_name1", "last_name2"] and not validator.is_valid_name_and_last_name(data[field]):
                        continue
                    if field == "phone" and not validator.is_valid_phone(data[field]):
                        continue
                    if field == "email" and not validator.is_valid_email(data[field]):
                        continue
                    if field == "password":
                        if not validator.is_valid_password(data["password"]):
                            continue
                        update_data["password"] = hash_password(data["password"])
                        continue
                    if field == "role":
                        new_role = data["role"]
                        target_role = target_doc.get("role", "user")
                        # Verificar que el rol actual puede asignar el nuevo rol
                        if not RolePermissions.can_assign_role(current_role, new_role):
                            return {"error": "You cannot assign this role"}, 403
                        # Verificar que el usuario actual puede actualizar al usuario sleccionado
                        if not RolePermissions.can_update_user(current_role, target_role):
                            return {"error": "You cannot update this user's role"}, 403

                        update_data["role"] = new_role
                        continue
                    update_data[field] = data[field]

            if update_data:
                users_collection.update_one({"_id": str(user_id)}, {"$set": update_data})
                logger.info(f"User {user_id} updated by {current_id}")
                return {"message": "User updated"}, 200

            return {"error": "No valid fields to update"}, 400

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    @staticmethod
    def delete_user(user_id: str):
        """
        Elimina un usuario. Extrae role del JWT.
        """
        try:
            current_id = get_jwt_identity()
            claims = get_jwt()
            current_role = claims.get("role", "user")

            target_doc = users_collection.find_one({"_id": str(user_id)})
            if not target_doc:
                return {"error": "User not found"}, 404

            target_role = target_doc.get("role", "user")
            if not RolePermissions.can_delete_user(current_role, target_role):
                return {"error": "You do not have permission to delete this user"}, 403

            users_collection.delete_one({"_id": str(user_id)})
            logger.info(f"User deleted: {user_id} by {current_id}")
            return {"message": "User deleted"}, 200

        except Exception as e:
            logger.error(f"Error in delete_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    @staticmethod
    def login_user(email: str, password: str):
        """
        Login de usuario usando email.
        Busca el usuario por email, obtiene su _id y genera token.
        """
        try:
            user_doc = users_collection.find_one({"email": email})
            if not user_doc:
                return {"error": "Email o contraseña incorrectos"}, 404

            if not verify_password(user_doc.get("password", ""), password):
                return {"error": "Email o contraseña incorrectos"}, 401

            user_id = str(user_doc["_id"])  # usamos el _id real
            role = user_doc.get("role", "user")
            access_token = generate_token(user_id, role)

            logger.info(f"User logged in: {email} with role {role}")
            return {
                "message": "Login exitoso",
                "access_token": access_token,
                "user": {"id": user_id, "role": role, "email": email},
            }, 200
        except Exception as e:
            logger.error(f"Error in login_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500

    # ==============================
    # GET LOGGED USER
    # ==============================
    @staticmethod
    def get_logged_user():
        """
        Devuelve la información del usuario logueado.
        Extrae ID y rol directamente del JWT.
        """
        try:
            user_id = get_jwt_identity()  
            claims = get_jwt()            
            role = claims.get("role", "user")

            user_doc = users_collection.find_one({"_id": str(user_id)})
            if not user_doc:
                return {"error": "User not found"}, 404

            return {"id": str(user_doc["_id"]), "role": role}, 200

        except Exception as e:
            logger.error(f"Error in get_logged_user: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500


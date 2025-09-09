import re
from app.models.user import users_collection


class UserValidator:
    def __init__(self, collection=None):
        """
        Validator adaptado para MongoDB
        """
        if collection is not None:
            self.collection = collection
        else:
            from app.models.user import users_collection
            self.collection = users_collection


    # ---------------------------
    # Utilidades
    # ---------------------------
    def _match_pattern(self, pattern: str, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return re.match(pattern, value) is not None

    def is_present(self, value):
        return isinstance(value, str) and value.strip() != ""

    # ---------------------------
    # Document (_id en MongoDB)
    # ---------------------------
    def is_valid_document(self, document) -> bool:
        if not self.is_present(document):
            return False
        pattern = r"^[0-9]{6,15}$"
        return self._match_pattern(pattern, str(document))

    def is_document_registered(self, document: str) -> bool:
        """
        Verifica si ya existe un usuario con ese _id en MongoDB
        """
        return self.collection.find_one({"_id": str(document)}) is not None

    # ---------------------------
    # Document Type
    # ---------------------------
    def is_valid_document_type(self, document_type) -> bool:
        if not self.is_present(document_type):
            return False
        valid_types = {"CC", "TI", "CE", "PA", "RC", "NUIP", "PEP", "PPT", "NIT"}
        return document_type in valid_types

    # ---------------------------
    # Role
    # ---------------------------
    def is_valid_role(self, role) -> bool:
        if not self.is_present(role):
            return False
        if not isinstance(role, str):
            return False
        return role in {"admin", "master", "user"}

    # ---------------------------
    # Name
    # ---------------------------
    def is_valid_name(self, name) -> bool:
        pattern = r"^[a-zA-Z]+$"
        return self._match_pattern(pattern, name)

    # ---------------------------
    # Last Names
    # ---------------------------
    def is_valid_last_name(self, last_name) -> bool:
        pattern = r"^[a-zA-Z]+$"
        return self._match_pattern(pattern, last_name)

    # ---------------------------
    # Email
    # ---------------------------
    def is_valid_email(self, email) -> bool:
        if not self.is_present(email):
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$"
        return self._match_pattern(pattern, email)

    def is_email_registered(self, email: str) -> bool:
        """
        Verifica si ya existe un usuario con ese email en MongoDB
        """
        return self.collection.find_one({"email": email}) is not None

    # ---------------------------
    # Phone
    # ---------------------------
    def is_valid_phone(self, phone) -> bool:
        if not self.is_present(str(phone)):
            return False
        pattern = r"^[0-9]{7,15}$"
        return self._match_pattern(pattern, str(phone))

    # ---------------------------
    # Password
    # ---------------------------
    def is_valid_password(self, password) -> bool:
        if not self.is_present(password):
            return False
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]{8,}$"
        return self._match_pattern(pattern, password)

    def is_valid_re_password(self, password, re_password) -> bool:
        return isinstance(password, str) and password == re_password

import re

class UserValidator:
    def __init__(self, db):
        """
        Initializes the validator with a Firestore database instance
        """
        self.db = db


    # Utility method to validate strings using a regular expression pattern
    def _match_pattern(self, pattern: str, value: str) -> bool:
        """
        Returns True if the given value matches the regex pattern
        """
        if not isinstance(value, str):
            return False
        return re.match(pattern, value) is not None


    def is_present(self, value):
        """
        Returns True if the value is a non-empty string
        Used to validate required input fields
        """
        return isinstance(value, str) and value.strip() != ""


    # ---------------------------
    # Document (used as document ID in Firestore)
    # ---------------------------
    def is_valid_document(self, document) -> bool:
        """
        Validates that the document consists of 6 to 15 numeric digits
        """
        if not self.is_present(document):
            return False
        pattern = r"^[0-9]{6,15}$"
        return self._match_pattern(pattern, str(document))

    def is_document_registered(self, document):
        """
        Checks if a document ID is already registered in Firestore
        """
        doc_ref = self.db.collection("users").document(str(document)).get()
        return doc_ref.exists


    # ---------------------------
    # Document Type
    # ---------------------------
    def is_valid_document_type(self, document_type) -> bool:
        """
        Validates that the document type is one of the allowed values
        """
        if not self.is_present(document_type):
            return False
        valid_types = {
            "CC", "TI", "CE", "PA", "RC", "NUIP", "PEP", "PPT", "NIT"
        }
        return document_type in valid_types


    # ---------------------------
    # Role
    # ---------------------------
    def is_valid_role(self, role) -> bool:
        """
        Validates that the role is 'admin'
        """
        if not self.is_present(role):
            return False
        if not isinstance(role, str):
            return False
        return role == 'admin'


    # ---------------------------
    # Name
    # ---------------------------
    def is_valid_name(self, name) -> bool:
        """
        Validates that the name contains only alphabetic characters
        """
        pattern = r"^[a-zA-Z]+$"
        return self._match_pattern(pattern, name)


    # ---------------------------
    # Last Names
    # ---------------------------
    def is_valid_last_name(self, last_name) -> bool:
        """
        Validates that the last name contains only alphabetic characters
        """
        pattern = r"^[a-zA-Z]+$"
        return self._match_pattern(pattern, last_name)


    # ---------------------------
    # Email
    # ---------------------------
    def is_valid_email(self, email) -> bool:
        """
        Validates that the email has a proper format (e.g., user@example.com)
        """
        if not self.is_present(email):
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$"
        return self._match_pattern(pattern, email)

    def is_email_registered(self, email) -> bool:
        """
        Checks if the email is already registered in Firestore
        """
        existing_users = self.db.collection("users").where("email", "==", email).stream()
        return any(existing_users)


    # ---------------------------
    # Phone
    # ---------------------------
    def is_valid_phone(self, phone) -> bool:
        """
        Validates that the phone number contains 7 to 15 numeric digits
        """
        if not self.is_present(phone):
            return False
        pattern = r"^[0-9]{7,15}$"
        return self._match_pattern(pattern, str(phone))


    # ---------------------------
    # Password
    # ---------------------------
    def is_valid_password(self, password) -> bool:
        """
        Validates that the password has at least 8 characters, including
        one uppercase letter, one lowercase letter, one digit, and one special character
        """
        if not self.is_present(password):
            return False
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]{8,}$"
        return self._match_pattern(pattern, password)
    
    def is_valid_re_password(self, password, re_password)  -> bool:
        """
        Checks if the password and confirmation password match exactly
        """
        return isinstance(password, str) and password == re_password

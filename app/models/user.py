class User:
    def __init__(self, document: str, document_type: str, role: str, name: str, last_name1: str, last_name2: str, email: str, password: str, phone: int):
        self.document = document 
        self.document_type = document_type
        self.role = role
        self.name = name
        self.last_name1 = last_name1
        self.last_name2 = last_name2
        self.email = email
        self.password = password
        self.phone = phone
        
    
    def to_dict(self):
        """
        Converts the User object into a dictionary to be stored in Firestore
        Excludes fields like password confirmation and document ID (used as document name)
        """
        return {
            'document_type': self.document_type,
            'role': self.role,
            'name': self.name,
            'last_name1': self.last_name1,
            'last_name2': self.last_name2,
            'email': self.email,
            'password': self.password,
            'phone': self.phone
        }

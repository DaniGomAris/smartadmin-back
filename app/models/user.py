from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class User:
    id: str
    document_type: str
    role: str
    name: str
    last_name1: str
    last_name2: str
    email: str
    phone: str
    password: Optional[str] = None

    def to_dict(self):
        data = {
            'document_type': self.document_type,
            'role': self.role,
            'name': self.name,
            'last_name1': self.last_name1,
            'last_name2': self.last_name2,
            'email': self.email,
            'password': self.password,
            'phone': self.phone
        }



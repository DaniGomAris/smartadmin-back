from app.utils.user_validator import UserValidator

validator = UserValidator(None)

# ------------------------------
# Document
# ------------------------------
def test_valid_document():
    assert validator.is_valid_document("000456")
    assert validator.is_valid_document("987654321")
    assert validator.is_valid_document("123456789012345") 

def test_invalid_document():
    assert not validator.is_valid_document("12a34")
    assert not validator.is_valid_document(" ")
    assert not validator.is_valid_document("")
    assert not validator.is_valid_document("123 456")
    assert not validator.is_valid_document("1234567890123456")  


# ------------------------------
# Document Type
# ------------------------------
def test_valid_document_type():
    assert validator.is_valid_document_type("CC")
    assert validator.is_valid_document_type("TI")
    assert validator.is_valid_document_type("NIT")

def test_invalid_document_type():
    assert not validator.is_valid_document_type("cc") 
    assert not validator.is_valid_document_type("DNI")
    assert not validator.is_valid_document_type("")
    assert not validator.is_valid_document_type("123")


# ------------------------------
# Role
# ------------------------------
def test_valid_role():
    assert validator.is_valid_role("admin")

def test_invalid_role():
    assert not validator.is_valid_role("Admin")
    assert not validator.is_valid_role("user")
    assert not validator.is_valid_role("")
    assert not validator.is_valid_role(None)
    
    
# ------------------------------
# Name
# ------------------------------
def test_valid_name():
    assert validator.is_valid_name("Juan")
    assert validator.is_valid_name("Maria")

def test_invalid_name():
    assert not validator.is_valid_name("Juan1")
    assert not validator.is_valid_name("Juan!")
    assert not validator.is_valid_name("Juan Pérez") 
    assert not validator.is_valid_name("")


# ------------------------------
# Last Name
# ------------------------------
def test_valid_last_name():
    assert validator.is_valid_last_name("Gomez")
    assert validator.is_valid_last_name("Lopez")

def test_invalid_last_name():
    assert not validator.is_valid_last_name("123")
    assert not validator.is_valid_last_name("Gómez!")
    assert not validator.is_valid_last_name("Ana María") 
    assert not validator.is_valid_last_name("")


# ------------------------------
# Email
# ------------------------------
def test_valid_email():
    assert validator.is_valid_email("test@example.com")
    assert validator.is_valid_email("user.name@mail.co")
    assert validator.is_valid_email("test_123@domain.net")

def test_invalid_email():
    assert not validator.is_valid_email("test@")
    assert not validator.is_valid_email("user@.com")
    assert not validator.is_valid_email("user@com")
    assert not validator.is_valid_email("user.com")
    assert not validator.is_valid_email("")


# ------------------------------
# Phone
# ------------------------------
def test_valid_phone():
    assert validator.is_valid_phone("3124567890")
    assert validator.is_valid_phone("1234567")
    assert validator.is_valid_phone("123456789012345") 

def test_invalid_phone():
    assert not validator.is_valid_phone("123456")          
    assert not validator.is_valid_phone("1234567890123456") 
    assert not validator.is_valid_phone("123-456-7890")    
    assert not validator.is_valid_phone("hola123")          
    assert not validator.is_valid_phone("")


# ------------------------------
# Password
# ------------------------------
def test_valid_password():
    assert validator.is_valid_password("Hola123@")
    assert validator.is_valid_password("ClaveSegura1!")
    assert validator.is_valid_password("XyZ$7890")

def test_invalid_password_format():
    assert not validator.is_valid_password("hola123")       
    assert not validator.is_valid_password("HOLA123!")      
    assert not validator.is_valid_password("Hola!")         
    assert not validator.is_valid_password("Hola123456")     
    assert not validator.is_valid_password("")               


# ------------------------------
# Re Password
# ------------------------------
def test_valid_re_password():
    assert validator.is_valid_re_password("Hola123@", "Hola123@")
    assert validator.is_valid_re_password("ClaveSegura1!", "ClaveSegura1!")
    assert validator.is_valid_re_password("XyZ$7890", "XyZ$7890")

def test_invalid_re_password():
    assert not validator.is_valid_re_password("Hola123@", "dwadafaw")
    assert not validator.is_valid_re_password("ClaveSegura1!", "dawgqwa")
    assert not validator.is_valid_re_password("XyZ$7890", "fqwasw")

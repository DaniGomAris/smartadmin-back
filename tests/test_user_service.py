import pytest
from unittest.mock import MagicMock
from app.services.user_service import UserService
from app.models.user import User
from app.auth.password_handler import hash_password

# Mock Firestore DB
mock_db = MagicMock()
service = UserService(mock_db)


# ------------------------------
# Test creación de usuario
# ------------------------------
def test_create_user_success():
    mock_db.collection().document().get.return_value.exists = False
    mock_db.collection().where().stream.return_value = []

    user_data = User(
        document="123456",
        document_type="CC",
        role="user",
        name="Juan",
        last_name1="Gomez",
        last_name2="Lopez",
        email="juan@example.com",
        password="Hola123@",
        phone="3001234567"
    )

    result = service.create_user(user_data, current_role="admin")
    assert result["id"] == user_data.document
    mock_db.collection().document().set.assert_called_once()


def test_create_user_conflict_document():
    mock_db.collection().document().get.return_value.exists = True
    user_data = User("123456", "CC", "user", "Juan", "Gomez", "Lopez", "juan@example.com", "Hola123@", "3001234567")
    with pytest.raises(Exception):
        service.create_user(user_data, current_role="admin")


def test_create_user_conflict_email():
    mock_db.collection().document().get.return_value.exists = False
    mock_db.collection().where().stream.return_value = [MagicMock()]

    user_data = User("123456", "CC", "user", "Juan", "Gomez", "Lopez", "juan@example.com", "Hola123@", "3001234567")
    with pytest.raises(Exception):
        service.create_user(user_data, current_role="admin")


def test_create_user_unauthorized_role():
    mock_db.collection().document().get.return_value.exists = False
    mock_db.collection().where().stream.return_value = []

    user_data = User("123456", "CC", "admin", "Juan", "Gomez", "Lopez", "juan@example.com", "Hola123@", "3001234567")
    with pytest.raises(Exception):
        service.create_user(user_data, current_role="admin")  # Admin cannot create admin


# ------------------------------
# Test login
# ------------------------------
def test_login_success():
    hashed = hash_password("Hola123@")
    user_doc = MagicMock()
    user_doc.to_dict.return_value = {
        "password": hashed,
        "role": "user",
        "email": "juan@example.com",
        "name": "Juan",
        "last_name1": "Gomez",
        "last_name2": "Lopez",
        "phone": "3001234567"
    }
    user_doc.id = "123456"
    mock_db.collection().where().stream.return_value = [user_doc]

    user_info, token = service.login("juan@example.com", "Hola123@")
    assert user_info["email"] == "juan@example.com"
    assert "access_token" in token


def test_login_user_not_found():
    mock_db.collection().where().stream.return_value = []
    with pytest.raises(Exception):
        service.login("noone@example.com", "Hola123@")


def test_login_invalid_password():
    hashed = hash_password("Hola123@")
    user_doc = MagicMock()
    user_doc.to_dict.return_value = {"password": hashed, "role": "user"}
    user_doc.id = "123456"
    mock_db.collection().where().stream.return_value = [user_doc]

    with pytest.raises(Exception):
        service.login("juan@example.com", "wrongpassword")


# ------------------------------
# Test delete user
# ------------------------------
def test_delete_user_success():
    target_doc = MagicMock()
    target_doc.exists = True
    target_doc.to_dict.return_value = {"role": "user"}
    mock_db.collection().document().get.return_value = target_doc

    result = service.delete_user("123456", current_role="admin")
    assert result["message"] == "User deleted"
    mock_db.collection().document().delete.assert_called_once()


def test_delete_user_unauthorized():
    target_doc = MagicMock()
    target_doc.exists = True
    target_doc.to_dict.return_value = {"role": "admin"}
    mock_db.collection().document().get.return_value = target_doc

    with pytest.raises(Exception):
        service.delete_user("123456", current_role="admin")


# ------------------------------
# Test update user
# ------------------------------
def test_update_user_success():
    target_doc = MagicMock()
    target_doc.exists = True
    target_doc.to_dict.return_value = {"role": "user"}
    mock_db.collection().document().get.return_value = target_doc

    update_data = {"name": "Pedro", "phone": "3120000000"}
    result = service.update_user("123456", update_data, current_role="admin")
    assert result["message"] == "User updated"
    mock_db.collection().document().update.assert_called_once()


def test_update_user_no_permission():
    target_doc = MagicMock()
    target_doc.exists = True
    target_doc.to_dict.return_value = {"role": "admin"}
    mock_db.collection().document().get.return_value = target_doc

    with pytest.raises(Exception):
        service.update_user("123456", {"name": "Pedro"}, current_role="admin")


# ------------------------------
# Test get logged user
# ------------------------------
def test_get_logged_user_success():
    user_doc = MagicMock()
    user_doc.exists = True
    user_doc.to_dict.return_value = {
        "email": "juan@example.com",
        "name": "Juan",
        "role": "user"
    }
    user_doc.id = "123456"
    mock_db.collection().document().get.return_value = user_doc

    result = service.get_logged_user("123456")
    assert result["id"] == "123456"
    assert result["email"] == "juan@example.com"


def test_get_logged_user_not_found():
    user_doc = MagicMock()
    user_doc.exists = False
    mock_db.collection().document().get.return_value = user_doc

    with pytest.raises(Exception):
        service.get_logged_user("123456")

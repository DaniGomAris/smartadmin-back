from flask import request, jsonify
from app.services.user_service import UserService

service = UserService()

class AuthController:

    @staticmethod
    def login_user():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        response, status = service.login_user(email, password)
        return jsonify(response), status


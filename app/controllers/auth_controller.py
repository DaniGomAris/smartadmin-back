from flask import request, jsonify
from app.services.user_service import UserService

service = UserService()

class AuthController:

    @staticmethod
    def login_user():
        data = request.get_json()
        document = data.get("document")
        password = data.get("password")
        response, status = service.login_user(document, password)
        return jsonify(response), status

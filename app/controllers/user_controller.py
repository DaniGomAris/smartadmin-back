from flask import request, jsonify
from app.services.user_service import UserService

service = UserService()

class UserController:
    
    @staticmethod
    def get_all_users():
        return jsonify(service.get_all_users())

    @staticmethod
    def get_all_users_console():
        return service.get_all_users_console()

    @staticmethod
    def get_users(user_id, role):
        return jsonify(service.get_users(role))

    @staticmethod
    def add_user(user_id, role):
        data = request.get_json()
        response, status = service.add_user(role, data)
        return jsonify(response), status

    @staticmethod
    def update_user(user_id, role, target_id):
        data = request.get_json()
        response, status = service.update_user({"role": role, "id": user_id}, target_id, data)
        return jsonify(response), status

    @staticmethod
    def delete_user(user_id, role, target_id):
        response, status = service.delete_user({"role": role, "id": user_id}, target_id)
        return jsonify(response), status

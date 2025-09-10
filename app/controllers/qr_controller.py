from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.services.qr_service import QRService

service = QRService()

class QRController:

    @staticmethod
    def generate_qr():
        """
        Genera un QR con un token temporal para el usuario actual
        """
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role", "user")

        qr_data = service.generate_qr_for_user(user_id)
        return jsonify(qr_data), 200

    @staticmethod
    def validate_qr():
        """
        Valida un QR enviado desde el frontend
        """
        data = request.get_json()
        token = data.get("token")
        if not token:
            return jsonify({"error": "No token provided"}), 400

        # Verifica el JWT y que el user_id exista en la DB
        result = service.validate_qr(token)
        if not result:
            return jsonify({"error": "Invalid or expired QR token"}), 401

        return jsonify(result), 200

import io
import qrcode
import base64

from flask_jwt_extended import get_jwt  
from app.auth.jwt_auth import generate_temporary_token, verify_token
from app.config.mongo_config import db

users_collection = db["users"]

class QRService:

    @staticmethod
    def generate_qr_for_user(user_id):
        """
        Genera un JWT temporal para el QR usando user_id y role,
        y lo convierte en QR base64
        """
        claims = get_jwt()
        role = claims.get("role", "user")

        # Genera un token temporal (10 minutos)
        token = generate_temporary_token(user_id, role)

        # Genera el QR
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convierte a base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {"qr_token": img_str, "token": token}

    @staticmethod
    def validate_qr(token):
        """
        Valida un JWT temporal y verifica que el user_id exista en la base de datos.
        """
        payload = verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        user_doc = users_collection.find_one({"_id": str(user_id)})
        if not user_doc:
            return None

        # Devuelve user_id y rol si todo es válido
        return {"user_id": user_id, "role": payload.get("role")}

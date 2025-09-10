from flask import Blueprint
from app.controllers.qr_controller import QRController
from app.decorators.auth_decorators import token_required

qr_bp = Blueprint("qr", __name__)

# Generar QR (solo usuarios autenticados)
qr_bp.route("/generate-qr", methods=["GET"])(token_required(QRController.generate_qr))

# Validar QR (no necesita token, porque el QR ya contiene el JWT temporal)
qr_bp.route("/validate", methods=["POST"])(QRController.validate_qr)

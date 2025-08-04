from functools import wraps
from flask import jsonify
from app.services.firebase import db
from flask_jwt_extended import get_jwt_identity

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        if user_data.get("role") != "admin":
            return jsonify({"error": "Unauthorized – Admin only"}), 403

        return fn(*args, **kwargs)
    return wrapper

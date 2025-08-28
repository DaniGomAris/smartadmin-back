# app/auth/jwt_handler.py

from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, decode_token
from flask import current_app


class JWTHandler:
    """
    Utility class to manage JWT creation and validation.
    """

    @staticmethod
    def create_token(identity: str, expires_minutes: int = 60) -> str:
        """
        Creates a JWT access token for the given identity.
        
        :param identity: Unique identifier for the token (usually user_id or email).
        :param expires_minutes: Expiration time in minutes.
        :return: Encoded JWT token as a string.
        """
        expires = timedelta(minutes=expires_minutes)
        return create_access_token(identity=identity, expires_delta=expires)

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes a JWT and returns its payload if valid.
        
        :param token: JWT string to decode.
        :return: Dictionary with decoded token claims.
        :raises Exception: If token is invalid or expired.
        """
        try:
            decoded = decode_token(token)
            return decoded
        except Exception as e:
            current_app.logger.error(f"JWT decoding failed: {str(e)}")
            raise

    @staticmethod
    def is_token_expired(decoded_token: dict) -> bool:
        """
        Checks if the given decoded token has expired.
        
        :param decoded_token: Token payload (from decode_token).
        :return: True if expired, False otherwise.
        """
        exp_timestamp = decoded_token.get("exp")
        if exp_timestamp is None:
            return True
        current_time = datetime.now(timezone.utc).timestamp()
        return current_time > exp_timestamp

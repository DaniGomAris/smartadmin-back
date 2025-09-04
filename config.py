import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def parse_timedelta(env_var, default=None):
    value = os.getenv(env_var, default)
    if value is None or str(value).lower() == "none":
        return False
    try:
        return timedelta(seconds=int(value))
    except ValueError:
        raise ValueError(f"La variable {env_var} debe ser un entero en segundos o 'none'")

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key")

    JWT_ACCESS_TOKEN_EXPIRES = parse_timedelta("JWT_ACCESS_TOKEN_EXPIRES", "none")
    JWT_REFRESH_TOKEN_EXPIRES = parse_timedelta("JWT_REFRESH_TOKEN_EXPIRES", "none")

    FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=5)

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

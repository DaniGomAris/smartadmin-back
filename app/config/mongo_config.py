# app/config/mongo_config.py
from pymongo import MongoClient
from app.config.app_config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

try:
    client.admin.command("ping")
    print(f"✅ Conectado a MongoDB")
except Exception as e:
    print("❌ Error al conectar con MongoDB:", e)

# app/config/mongo_config.py
from pymongo import MongoClient
from app.config.config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# ---- TEST DE CONEXIÓN ----
try:
    client.admin.command("ping")
    print(f"✅ Conectado a MongoDB en {Config.MONGO_URI}, usando DB: {Config.DB_NAME}")
except Exception as e:
    print("❌ Error al conectar con MongoDB:", e)

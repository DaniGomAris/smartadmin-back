from pymongo import MongoClient
from app.config.app_config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

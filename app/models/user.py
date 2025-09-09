from app.config.mongo_config import db

# Conexión a la colección de usuarios en Mongo
users_collection = db["users"]

class UserModel:
    @staticmethod
    def create_user(user_data: dict):
        """
        Inserta un nuevo usuario en MongoDB
        """
        return users_collection.insert_one(user_data)

    @staticmethod
    def find_by_id(user_id: str):
        """
        Busca un usuario por su _id (string)
        """
        return users_collection.find_one({"_id": str(user_id)})

    @staticmethod
    def find_by_email(email: str):
        """
        Busca un usuario por email
        """
        return users_collection.find_one({"email": email})

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        """
        Actualiza los datos de un usuario
        """
        return users_collection.update_one(
            {"_id": str(user_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete_user(user_id: str):
        """
        Elimina un usuario por _id
        """
        return users_collection.delete_one({"_id": str(user_id)})

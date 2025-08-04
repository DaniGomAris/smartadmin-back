import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Ruta correcta al secret file en Render
# firebase_key_path = "/etc/secrets/firebase_key.json"

# Ruta correcta al secret file en local
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

# Inicializar Firestore
db = firestore.client()

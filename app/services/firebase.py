import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Route to secret file(Render)
#firebase_key_path = "/etc/secrets/firebase_key.json"

# Route to secret file (local)
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
deployment = os.getenv("NODE_ENV")

if os.getenv("NODE_ENV") == "cloud":
    firebase_key_path = "/etc/secrets/firebase_key.json"
else:
    if os.getenv("NODE_ENV") == "local":
        firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
    else:
        raise ValueError("NODE_ENV must be set to 'local' or 'cloud'")

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
deployment = os.getenv("NODE_ENV")

if deployment == "production":
    firebase_key_path = os.getenv("FIREBASE_KEY_PATH_PROD")
elif deployment == "development":
    firebase_key_path = os.getenv("FIREBASE_KEY_PATH_DEV")
else:
    raise ValueError("NODE_ENV must be set to 'development' or 'production'")

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

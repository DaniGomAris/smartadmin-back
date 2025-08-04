# 💊 SmartAdmin

**SmartPill** is a web page that helps users manage their towers. This repository includes both the **backend (Flask + Firebase)** and the **frontend (Angular)** of the project.

---

## ⚙️ Backend (Flask)

### 🔧 Requirements

- Python 3.10 or higher
- Virtualenv (recommended) (.\venv\Scripts\activate)
- Firebase project with service account key

## 🔧 Firestore Setup Guide

This project uses Firebase Firestore to store user data. Since the database key (`firebase_key.json`) is private and not included for security reasons, follow these steps to connect your own Firestore instance.

---

### ✅ Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Choose a name (e.g., `smartpill-demo`) and follow the instructions
4. You can skip Google Analytics setup

---

### 🔥 Step 2: Enable Firestore

1. In the Firebase Console, go to **"Build" > "Firestore Database"**
2. Click **"Create database"**
3. Select **Start in test mode** (or production if preferred)
4. Pick a region and click **"Enable"**

---

### 📁 Step 3: Create the `users` Collection

1. Click **"Start collection"**
2. Use `users` as the collection name
3. Add a dummy document with the following fields (all type **string**):

| Field         | Example Value         |
|---------------|------------------------|
| document      | "123456"               |
| document_type | "CC"                   |
| name          | "John"                 |
| last_names    | "Doe"                  |
| email         | "john@example.com"     |
| password      | "hashedpassword"       |
| years         | "28"                   |

You can delete this dummy later — it’s just to initialize the structure.

---

### 🔐 Step 4: Generate Admin SDK Key

1. Go to **"Project settings"** (gear icon)
2. Click **"Service accounts"** tab
3. Click **"Generate new private key"**
4. This will download a `.json` file
5. Rename it to `firebase_key.json` and place it in the `backend/` folder

### 🛠️ Step 5: Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the `backend/` folder:
   ```env
   FIREBASE_KEY_PATH=firebase_key.json
   JWT_SECRET_KEY=your-secret-key
   ```

5. **Run the backend server**:
   ```bash
   python app.py
   ```

---

## 🔐 Authentication

- Authentication is handled via **JWT (JSON Web Tokens)**.
- Passwords are securely **hashed** using `werkzeug.security` before storing them in Firebase.

---

## 🧪 Testing

All unit tests are located in the `backend/tests/` directory.

To run a test file:
```bash
python tests/test_firebase.py
```

---

## 📂 Git Best Practices

- All sensitive files like `.env` and `firebase_key.json` are ignored via `.gitignore`.
- Use branches for features and open Pull Requests when merging into `main`.

---

## 📄 License

This project is for educational and demonstration purposes. Feel free to use, modify, and extend it as needed

---

## 📬 Contact

Author:
GitHub: DaniGomAris

---
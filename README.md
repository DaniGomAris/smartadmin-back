# SmartAdmin Backend

Backend construido con **Flask**, **Firebase Firestore** y gestión de autenticación mediante **JWT**.

---

## 🚀 Tecnologías

- Python 3.10+
- Flask
- Firebase Admin SDK (Firestore)
- Flask-JWT-Extended (JWT)
- Argon2 (hash de contraseña)
- Docker (opcional)

---

### Variables de entorno (usa `.env`)

```
FIREBASE_KEY_PATH=path/to/firebase_key.json
JWT_SECRET_KEY=tu_clave_secreta
FLASK_ENV=development
```

---

## ▶️ Ejecutar

```bash
python app.py
```

La app estará disponible en `http://127.0.0.1:5000`.

---

## 📌 Endpoints principales

| Método | Ruta             | Roles permitidos        | Descripción                        |
|--------|------------------|--------------------------|-------------------------------------|
| POST   | `/users/login`   | —                        | Login: recibe email y contraseña, retorna JWT |
| GET    | `/users/me`      | Autenticado              | Info del usuario autenticado        |
| GET    | `/users/`        | Admin/Master             | Listar usuarios                     |
| POST   | `/users/`        | Admin/Master             | Crear usuario (Master puede asignar roles Admin/User; Admin solo User) |
| PUT    | `/users/<id>`    | Admin/Master             | Actualizar usuario según jerarquía |
| DELETE | `/users/<id>`    | Admin/Master             | Eliminar usuario según rol         |

---

## 🧩 Modelo de datos (`models/User.py`)

```python
class User:
    def __init__(...):
        ...

    def to_dict(self):
        return {
          "document_type": self.document_type,
          "role": self.role,
          ...
        }
```

---

## 🔒 Seguridad

- Contraseñas almacenadas con **Argon2**.
- Autorización por roles `user`, `admin`, `master`.
- Límites antifuerza bruta usando `flask-limiter`.

---

## 🧪 Testing

Ejecuta los tests con:

```bash
pytest
```

---

## 📄 Licencia


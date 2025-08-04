import uuid
from app.services.firebase import db

def test_firestore_connection_read_write_delete():
    """
    Check connection to Firestone by writing, reading and deleting a temporary document
    """
    test_collection = "test_connection"
    test_doc_id = str(uuid.uuid4()) 
    test_data = {"message": "test successful"}

    try:
        # Create temporal document
        db.collection(test_collection).document(test_doc_id).set(test_data)

        # Read document
        doc = db.collection(test_collection).document(test_doc_id).get()
        assert doc.exists, "Documento no fue creado correctamente"
        assert doc.to_dict() == test_data, "Datos del documento no coinciden"

        # Delete document
        db.collection(test_collection).document(test_doc_id).delete()

    except Exception as e:
        assert False, f"Error en conexión con Firestore: {e}"

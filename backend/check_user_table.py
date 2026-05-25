from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    with db.engine.connect() as conn:
        # Vérifier la structure de la table user
        try:
            result = conn.execute(text("SHOW TABLES LIKE 'user'")).fetchall()
            print(f"SHOW TABLES LIKE 'user': {result}")
        except Exception as e:
            print(f"Erreur SHOW TABLES: {e}")
        
        # Vérifier les tables existantes
        result = conn.execute(text("SHOW TABLES")).fetchall()
        print(f"\nToutes les tables: {[r[0] for r in result]}")
        
        # Vérifier les en-têtes de la table user si elle existe
        try:
            result = conn.execute(text("DESCRIBE user")).fetchall()
            print(f"\nSTRUCTURE de 'user':\n{result}")
        except Exception as e:
            print(f"\nErreur DESCRIBE user: {type(e).__name__}: {e}")

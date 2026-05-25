"""
Script simpler - vérifier et répéter jusqu'à ce que ça marche
"""
from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    print("=== TENTATIVE DE FIX DIRECTE + VÉRIFICATION ===\n")
    
    # Passer par inspect pour lister les tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    # Vérifier les FK via SQLAlchemy inspector
    print("\nFK actuelles (selon SQLAlchemy inspector):")
    for table_name in tables:
        if table_name in ['rdv', 'planning']:
            fks = inspector.get_foreign_keys(table_name)
            print(f"  {table_name}:")
            for fk in fks:
                print(f"    {fk}")
    
    # Vérifier si user table existe dans le schéma SQLAlchemy
    print(f"\nTable 'user' dans session SQLAlchemy: {'user' in tables}")

from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        print("=== VÉRIFICATION FINALE ===\n")
        
        # 1. Liste des tables
        tables = conn.execute(text("SHOW TABLES")).fetchall()
        table_names = [r[0] for r in tables]
        print(f"Tables existantes: {table_names}")
        print(f"Table 'user' existe: {'user' in table_names}")
        
        # 2. ShowFK via SHOW CREATE TABLE
        print("\n=== FK dans RDV ===")
        try:
            rdv_create = conn.execute(text("SHOW CREATE TABLE rdv")).fetchone()
            # Afficher le CREATE TABLE entier
            create_sql = rdv_create[1]
            for line in create_sql.split('\n'):
                if 'CONSTRAINT' in line or 'FOREIGN' in line or 'REFERENCES' in line:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"Erreur: {e}")
        
        print("\n=== FK dans PLANNING ===")
        try:
            planning_create = conn.execute(text("SHOW CREATE TABLE planning")).fetchone()
            create_sql = planning_create[1]
            for line in create_sql.split('\n'):
                if 'CONSTRAINT' in line or 'FOREIGN' in line or 'REFERENCES' in line:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"Erreur: {e}")
        
        # 3. Les données
        print("\n=== DONNÉES ===")
        print(f"RDV: {conn.execute(text('SELECT COUNT(*) FROM rdv')).scalar()} enregistrements")
        print(f"Planning: {conn.execute(text('SELECT COUNT(*) FROM planning')).scalar()} enregistrements")
        print(f"Patient: {conn.execute(text('SELECT COUNT(*) FROM patient')).scalar()} enregistrements")
        print(f"Personnel de santé: {conn.execute(text('SELECT COUNT(*) FROM personnel_de_sante')).scalar()} enregistrements")

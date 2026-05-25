from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        print("Vérifier les données RDV et Planning:")
        
        # Vérifier le contenu de rdv
        rdv_count = conn.execute(text("SELECT COUNT(*), GROUP_CONCAT(idPatient), GROUP_CONCAT(idPersonnel) FROM rdv")).first()
        print(f"RDV: count={rdv_count[0]}, idPatient={rdv_count[1]}, idPersonnel={rdv_count[2]}")
        
        # Vérifier le contenu de planning
        planning_count = conn.execute(text("SELECT COUNT(*), GROUP_CONCAT(idPersonnel) FROM planning")).first()
        print(f"Planning: count={planning_count[0]}, idPersonnel={planning_count[1]}")
        
        # Vérifier les données dans patient et personnel_de_sante
        patient_count = conn.execute(text("SELECT COUNT(*) FROM patient")).scalar()
        personnel_count = conn.execute(text("SELECT COUNT(*) FROM personnel_de_sante")).scalar()
        user_count = conn.execute(text("SELECT COUNT(*) FROM user")).scalar()
        
        print(f"\nComptes des tables de référence:")
        print(f"  patient: {patient_count}")
        print(f"  personnel_de_sante: {personnel_count}")
        print(f"  user: {user_count}")

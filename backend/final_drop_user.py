from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.begin() as conn:
        print("1. Désactiver les vérifications de FK...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        
        print("2. Supprimer les FK qui pointent vers 'user'...")
        try:
            conn.execute(text("ALTER TABLE rdv DROP FOREIGN KEY fk_rdv_patient"))
            print("   ✓ rdv.fk_rdv_patient supprimée")
        except Exception as e:
            print(f"   ⚠ {e}")
        
        try:
            conn.execute(text("ALTER TABLE rdv DROP FOREIGN KEY fk_rdv_personnel"))
            print("   ✓ rdv.fk_rdv_personnel supprimée")
        except Exception as e:
            print(f"   ⚠ {e}")
        
        try:
            conn.execute(text("ALTER TABLE planning DROP FOREIGN KEY fk_planning_personnel"))
            print("   ✓ planning.fk_planning_personnel supprimée")
        except Exception as e:
            print(f"   ⚠ {e}")
        
        print("\n3. Supprimer la table 'user'...")
        conn.execute(text("DROP TABLE IF EXISTS user"))
        print("   ✓ Table 'user' supprimée")
        
        print("\n4. Recréer les FK vers les BONNES tables...")
        conn.execute(text("""
            ALTER TABLE rdv
            ADD CONSTRAINT fk_rdv_patient
            FOREIGN KEY (idPatient)
            REFERENCES patient(id_patient)
            ON DELETE RESTRICT ON UPDATE CASCADE
        """))
        print("   ✓ rdv.fk_rdv_patient -> patient")
        
        conn.execute(text("""
            ALTER TABLE rdv
            ADD CONSTRAINT fk_rdv_personnel
            FOREIGN KEY (idPersonnel)
            REFERENCES personnel_de_sante(id_personnel)
            ON DELETE RESTRICT ON UPDATE CASCADE
        """))
        print("   ✓ rdv.fk_rdv_personnel -> personnel_de_sante")
        
        conn.execute(text("""
            ALTER TABLE planning
            ADD CONSTRAINT fk_planning_personnel
            FOREIGN KEY (idPersonnel)
            REFERENCES personnel_de_sante(id_personnel)
            ON DELETE RESTRICT ON UPDATE CASCADE
        """))
        print("   ✓ planning.fk_planning_personnel -> personnel_de_sante")
        
        print("\n5. Réactiver les vérifications de FK...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        
        print("\n✅ Migration terminée avec succès!")

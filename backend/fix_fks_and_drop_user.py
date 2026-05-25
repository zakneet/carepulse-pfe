"""
Script pour corriger les FK incorrectes (qui pointent vers user)
et les recréer pour pointer vers patient et personnel_de_sante.
"""
from app import app, db

def fix_fks_and_drop_user():
    with app.app_context():
        try:
            with db.engine.begin() as conn:
                print("1. Désactiver les vérifications de FK...")
                conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0")
                
                print("2. Supprimer les contraintes FK incorrectes...")
                try:
                    conn.exec_driver_sql("ALTER TABLE rdv DROP FOREIGN KEY fk_rdv_patient")
                    print("   ✓ rdv.fk_rdv_patient supprimée")
                except Exception as e:
                    print(f"   ⚠ Erreur suppression fk_rdv_patient: {e}")
                
                try:
                    conn.exec_driver_sql("ALTER TABLE rdv DROP FOREIGN KEY fk_rdv_personnel")
                    print("   ✓ rdv.fk_rdv_personnel supprimée")
                except Exception as e:
                    print(f"   ⚠ Erreur suppression fk_rdv_personnel: {e}")
                
                try:
                    conn.exec_driver_sql("ALTER TABLE planning DROP FOREIGN KEY fk_planning_personnel")
                    print("   ✓ planning.fk_planning_personnel supprimée")
                except Exception as e:
                    print(f"   ⚠ Erreur suppression fk_planning_personnel: {e}")
                
                print("\n3. Créer les nouvelles FK vers patient et personnel_de_sante...")
                conn.exec_driver_sql("""
                    ALTER TABLE rdv
                    ADD CONSTRAINT fk_rdv_patient
                    FOREIGN KEY (idPatient)
                    REFERENCES patient(id_patient)
                    ON DELETE RESTRICT ON UPDATE CASCADE
                """)
                print("   ✓ rdv.fk_rdv_patient créée (->patient)")
                
                conn.exec_driver_sql("""
                    ALTER TABLE rdv
                    ADD CONSTRAINT fk_rdv_personnel
                    FOREIGN KEY (idPersonnel)
                    REFERENCES personnel_de_sante(id_personnel)
                    ON DELETE RESTRICT ON UPDATE CASCADE
                """)
                print("   ✓ rdv.fk_rdv_personnel créée (->personnel_de_sante)")
                
                conn.exec_driver_sql("""
                    ALTER TABLE planning
                    ADD CONSTRAINT fk_planning_personnel
                    FOREIGN KEY (idPersonnel)
                    REFERENCES personnel_de_sante(id_personnel)
                    ON DELETE RESTRICT ON UPDATE CASCADE
                """)
                print("   ✓ planning.fk_planning_personnel créée (->personnel_de_sante)")
                
                print("\n4. Réactiver les vérifications de FK...")
                conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1")
                
                print("\n5. Vérifier si la table 'user' existe...")
                result = conn.exec_driver_sql("""
                    SELECT COUNT(1) FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user'
                """).scalar()
                
                if result > 0:
                    print("   Table 'user' existe - suppression...")
                    conn.exec_driver_sql("DROP TABLE user")
                    print("   ✓ Table 'user' supprimée")
                else:
                    print("   Table 'user' n'existe pas - OK")
                
                print("\n✅ Migration terminée avec succès!")
                
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_fks_and_drop_user()

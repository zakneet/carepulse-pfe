from app import app, db
from sqlalchemy import text

def drop_user_safely():
    with app.app_context():
        print("=== SUPPRESSION SÉCURISÉE DE 'user' ===\n")
        
        try:
            with db.engine.begin() as conn:
                # 1. Désactiver FK
                print("1. Désactiver les vérifications de FK...")
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                print("   ✓ FK check désactivé\n")
                
                # 2. Afficher current FK
                print("2. FK actuelles AVANT suppression:")
                fks = conn.execute(text("""
                    SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE() AND CONSTRAINT_NAME LIKE 'fk_%'
                """)).fetchall()
                for fk in fks:
                    print(f"   {fk[0]}.{fk[2]} -> {fk[3]}.{fk[4]} [{fk[1]}]")
                
                # 3. Supprimer FK
                print("\n3. Supprimer les FK pointant vers 'user'...")
                
                # D'abord vérifier quelles FK existent
                alter_commands = [
                    ("rdv", "fk_rdv_patient"),
                    ("rdv", "fk_rdv_personnel"),
                    ("planning", "fk_planning_personnel"),
                ]
                
                for table, fk_name in alter_commands:
                    try:
                        sql = f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}"
                        print(f"   Exécution: {sql}")
                        conn.execute(text(sql))
                        print(f"   ✓ Supprimée: {table}.{fk_name}")
                    except Exception as e:
                        print(f"   ⚠ Erreur pour {table}.{fk_name}: {e}")
                
                # 4. Supprimer user
                print("\n4. Supprimer la table 'user'...")
                try:
                    conn.execute(text("DROP TABLE IF EXISTS user"))
                    print("   ✓ Supprimée ou n'existait pas")
                except Exception as e:
                    print(f"   ✗ ERREUR: {e}")
                
                # 5. Recréer FK
                print("\n5. Recréer les FK vers les BONNES tables...")
                new_fk_commands = [
                    ("""ALTER TABLE rdv
                        ADD CONSTRAINT fk_rdv_patient
                        FOREIGN KEY (idPatient)
                        REFERENCES patient(id_patient)
                        ON DELETE RESTRICT ON UPDATE CASCADE""", "rdv.fk_rdv_patient -> patient"),
                    ("""ALTER TABLE rdv
                        ADD CONSTRAINT fk_rdv_personnel
                        FOREIGN KEY (idPersonnel)
                        REFERENCES personnel_de_sante(id_personnel)
                        ON DELETE RESTRICT ON UPDATE CASCADE""", "rdv.fk_rdv_personnel -> personnel_de_sante"),
                    ("""ALTER TABLE planning
                        ADD CONSTRAINT fk_planning_personnel
                        FOREIGN KEY (idPersonnel)
                        REFERENCES personnel_de_sante(id_personnel)
                        ON DELETE RESTRICT ON UPDATE CASCADE""", "planning.fk_planning_personnel -> personnel_de_sante"),
                ]
                
                for sql, desc in new_fk_commands:
                    try:
                        conn.execute(text(sql))
                        print(f"   ✓ {desc}")
                    except Exception as e:
                        print(f"   ✗ ERREUR pour {desc}: {e}")
                
                # 6. Réactiver FK
                print("\n6. Réactiver les vérifications de FK...")
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                print("   ✓ FK check réactivé")
                
                print("\n✅ TERMINÉ - transactions seront commités automatiquement")
                
        except Exception as e:
            print(f"\n❌ ERREUR GLOBALE: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    drop_user_safely()

from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        # Vérifier que user n'existe plus
        result = conn.execute(text("""
            SELECT COUNT(1) FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user'
        """)).scalar()
        print(f"Table 'user' existe: {result > 0}")
        
        # Vérifier les FK actuelles
        print("\nContraintes FK actuelles:")
        rows = conn.execute(text("""
            SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND CONSTRAINT_NAME LIKE :pattern
            ORDER BY TABLE_NAME
        """), {"pattern": "fk_%"}).fetchall()
        for r in rows:
            print(f"  {r[0]}.{r[2]} -> {r[3]}.* [{r[1]}]")
        
        # Vérifier les colonnes clés des tables principales
        print("\nComptages:")
        for table in ['patient', 'personnel_de_sante', 'rdv', 'planning']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count} enregistrements")

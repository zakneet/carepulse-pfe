from app import app, db

query = """
SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME = 'user'
  AND TABLE_SCHEMA = DATABASE();
"""

with app.app_context():
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(query).fetchall()
        if not rows:
            print("NO_FK_REFERENCES")
        else:
            for r in rows:
                print(f"TABLE={r[0]}\tCONSTRAINT={r[1]}\tCOLUMN={r[2]}\tREFERENCED={r[3]}")

import mysql.connector

DB_NAME = "gestion_des_rendez-vous-3"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database=DB_NAME,
)
conn.autocommit = False
cur = conn.cursor()

try:
    # Ensure target table exists.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            id INT NOT NULL AUTO_INCREMENT,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            telephone VARCHAR(30) NULL,
            email VARCHAR(120) NULL,
            role INT NOT NULL,
            specialite VARCHAR(120) NULL,
            disponibilite VARCHAR(255) NULL,
            password VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (id),
            UNIQUE KEY uq_user_email (email)
        ) ENGINE=InnoDB
        """
    )

    # Discover legacy columns in users.
    cur.execute("SHOW TABLES LIKE 'users'")
    has_users = cur.fetchone() is not None

    if has_users:
        cur.execute("SHOW COLUMNS FROM users")
        cols = {row[0] for row in cur.fetchall()}

        select_id = "id" if "id" in cols else "NULL"
        select_nom = "nom" if "nom" in cols else "''"
        select_prenom = "prenom" if "prenom" in cols else "''"
        select_tel = "telephone" if "telephone" in cols else "NULL"
        select_email = "email" if "email" in cols else "NULL"
        select_role = "role" if "role" in cols else "1"
        select_spec = "specialite" if "specialite" in cols else "NULL"
        select_dispo = "disponibilite" if "disponibilite" in cols else "NULL"
        select_pwd = "password" if "password" in cols else "''"

        insert_sql = f"""
            INSERT INTO user (id, nom, prenom, telephone, email, role, specialite, disponibilite, password)
            SELECT {select_id}, {select_nom}, {select_prenom}, {select_tel}, {select_email}, {select_role}, {select_spec}, {select_dispo}, {select_pwd}
            FROM users
            ON DUPLICATE KEY UPDATE
                nom = VALUES(nom),
                prenom = VALUES(prenom),
                telephone = VALUES(telephone),
                email = VALUES(email),
                role = VALUES(role),
                specialite = VALUES(specialite),
                disponibilite = VALUES(disponibilite),
                password = VALUES(password)
        """
        cur.execute(insert_sql)

    # Drop existing FK constraints from planning/rdv (if any).
    cur.execute(
        """
        SELECT TABLE_NAME, CONSTRAINT_NAME
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = %s
          AND CONSTRAINT_TYPE = 'FOREIGN KEY'
          AND TABLE_NAME IN ('rdv', 'planning')
        """,
        (DB_NAME,),
    )
    for table_name, constraint_name in cur.fetchall():
        cur.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}")

    # Remove orphan rows before adding FK to user.
    cur.execute(
        "DELETE r FROM rdv r LEFT JOIN user u ON r.idPatient = u.id WHERE r.idPatient IS NOT NULL AND u.id IS NULL"
    )
    cur.execute(
        "DELETE r FROM rdv r LEFT JOIN user u ON r.idPersonnel = u.id WHERE r.idPersonnel IS NOT NULL AND u.id IS NULL"
    )
    cur.execute(
        "DELETE p FROM planning p LEFT JOIN user u ON p.idPersonnel = u.id WHERE p.idPersonnel IS NOT NULL AND u.id IS NULL"
    )

    # Recreate FKs to user table.
    cur.execute(
        "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_patient FOREIGN KEY (idPatient) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
    )
    cur.execute(
        "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_personnel FOREIGN KEY (idPersonnel) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
    )
    cur.execute(
        "ALTER TABLE planning ADD CONSTRAINT fk_planning_personnel FOREIGN KEY (idPersonnel) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
    )

    # Drop legacy users table.
    cur.execute("DROP TABLE IF EXISTS users")

    conn.commit()
    print("Migration OK: users -> user")

except Exception as exc:
    conn.rollback()
    raise

finally:
    cur.close()
    conn.close()

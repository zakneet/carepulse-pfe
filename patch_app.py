with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _ensure_personnel_table_columns DROP loop
content = content.replace(
    'for legacy_column in ("telephone", "email", "region", "ville", "type_personnel", "password", "access_code"):',
    'for legacy_column in ("telephone", "email", "ville", "type_personnel", "password", "access_code"):'
)

# 2. Add region column in _ensure_personnel_table_columns
if 'ALTER TABLE personnel_de_sante ADD COLUMN `region` VARCHAR(120) NULL' not in content:
    content = content.replace(
        'conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `specialite` VARCHAR(120) NULL")',
        'conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `specialite` VARCHAR(120) NULL")\n            try:\n                conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `region` VARCHAR(120) NULL")\n            except Exception:\n                pass'
    )

# 3. Add region column in migrate_mysql_schema
if 'region VARCHAR(120) NULL,' not in content:
    content = content.replace(
        'specialite VARCHAR(120) NULL,',
        'specialite VARCHAR(120) NULL,\n                    region VARCHAR(120) NULL,'
    )

# 4. Update get_medical_staff
old_staff_route = '''@app.route("/medical-staff", methods=["GET"])
@debug_route
def get_medical_staff():
    try:
        specialite = request.args.get('specialite', '')

        query = """
            SELECT id_personnel, nom, prenom, specialite, disponibilite
            FROM personnel_de_sante
            WHERE 1=1
        """
        params = []
        if specialite:
            query += " AND LOWER(specialite) LIKE LOWER(%s)"
            params.append(f"%{specialite}%")'''

new_staff_route = '''@app.route("/medical-staff", methods=["GET"])
@debug_route
def get_medical_staff():
    try:
        specialite = request.args.get('specialite', '')
        region = request.args.get('region', '')

        query = """
            SELECT id_personnel, nom, prenom, specialite, region, disponibilite
            FROM personnel_de_sante
            WHERE 1=1
        """
        params = []
        if specialite:
            query += " AND LOWER(specialite) LIKE LOWER(%s)"
            params.append(f"%{specialite}%")
        if region:
            query += " AND LOWER(region) LIKE LOWER(%s)"
            params.append(f"%{region}%")'''

content = content.replace(old_staff_route, new_staff_route)

# 5. Make sure the returned rows have region
content = content.replace(
    '"specialite": row["specialite"],',
    '"specialite": row["specialite"],\n                    "region": row.get("region"),'
)

# 6. Make sure _get_personnel_row returns region as well
content = content.replace(
    'SELECT id_personnel, nom, prenom, specialite, disponibilite',
    'SELECT id_personnel, nom, prenom, specialite, region, disponibilite'
)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

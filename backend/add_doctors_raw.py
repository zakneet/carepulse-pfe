import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='gestion_des_rendez-vous',
    cursorclass=pymysql.cursors.DictCursor
)

doctors_data = [
    {"nom": "Ben Salah", "prenom": "Amira", "specialite": "Médecine générale", "type_personnel": "medecin"},
    {"nom": "Trabelsi", "prenom": "Karim", "specialite": "Cardiologie", "type_personnel": "medecin"},
    {"nom": "Mansour", "prenom": "Leïla", "specialite": "Dermatologie", "type_personnel": "medecin"},
    {"nom": "Haddad", "prenom": "Youssef", "specialite": "Pédiatrie", "type_personnel": "medecin"},
    {"nom": "Gharbi", "prenom": "Sami", "specialite": "Dentaire", "type_personnel": "medecin"},
    {"nom": "Cherif", "prenom": "Nadia", "specialite": "Ophtalmologie", "type_personnel": "medecin"}
]

with connection:
    with connection.cursor() as cursor:
        for doc in doctors_data:
            cursor.execute("SELECT * FROM personnel_de_sante WHERE nom=%s AND prenom=%s", (doc["nom"], doc["prenom"]))
            result = cursor.fetchone()
            if not result:
                sql = "INSERT INTO personnel_de_sante (nom, prenom, specialite, type_personnel, password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (doc["nom"], doc["prenom"], doc["specialite"], doc["type_personnel"], ""))
                print(f"Added: Dr. {doc['prenom']} {doc['nom']}")
            else:
                print(f"Already exists: Dr. {doc['prenom']} {doc['nom']}")
        
    connection.commit()

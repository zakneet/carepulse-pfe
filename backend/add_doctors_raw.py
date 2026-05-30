import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='gestion_des-rendez-vous5',
    cursorclass=pymysql.cursors.DictCursor
)

doctors_data = [
    {"nom": "Ben Salah", "prenom": "Amira", "specialite": "Médecine générale"},
    {"nom": "Trabelsi", "prenom": "Karim", "specialite": "Cardiologie"},
    {"nom": "Mansour", "prenom": "Leïla", "specialite": "Dermatologie"},
    {"nom": "Haddad", "prenom": "Youssef", "specialite": "Pédiatrie"},
    {"nom": "Gharbi", "prenom": "Sami", "specialite": "Dentaire"},
    {"nom": "Cherif", "prenom": "Nadia", "specialite": "Ophtalmologie"}
]

with connection:
    with connection.cursor() as cursor:
        for doc in doctors_data:
            cursor.execute("SELECT * FROM personnel_de_sante WHERE nom=%s AND prenom=%s", (doc["nom"], doc["prenom"]))
            result = cursor.fetchone()
            if not result:
                sql = "INSERT INTO personnel_de_sante (nom, prenom, specialite, disponibilite) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (doc["nom"], doc["prenom"], doc["specialite"], 1))
                print(f"Added: Dr. {doc['prenom']} {doc['nom']}")
            else:
                print(f"Already exists: Dr. {doc['prenom']} {doc['nom']}")
        
    connection.commit()

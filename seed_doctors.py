import random
import pymysql

# Grouped regions provided by the user
regions_data = {
    "Tunis & Ariana": ["Carthage", "Bardo", "La Marsa", "Ariana Ville", "Soukra", "Raoued", "Cité Attadhamon"],
    "Ben Arous & Manouba": ["Radès", "Hammam Lif", "Mornag", "Manouba", "Oued Ellil", "Tebourba"],
    "Nabeul & Bizerte": ["Nabeul", "Hammamet", "Kelibia", "Bizerte Nord", "Menzel Bourguiba", "Ras Jebel"],
    "Zaghouan & Sousse": ["Zaghouan", "Fahs", "Sousse (Ryadh/Jawhara)", "Hammam Sousse", "Msaken", "Enfidha"],
    "Monastir & Mahdia": ["Monastir", "Moknine", "Ksar Helal", "Mahdia", "Eljem", "Chebba"],
    "Sfax": ["Sfax (Ville/Ouest/Sud)", "Sakiet Ezzit", "Agareb", "Mahrès", "Kerkennah"],
    "Nord-Ouest": ["Béja", "Testour", "Jendouba", "Tabarka", "Ain Drahem", "Kef", "Dahmani", "Siliana", "Makther"],
    "Centre-Ouest": ["Kairouan", "Haffouz", "Sidi Bouzid", "Regueb", "Kasserine", "Sbitla", "Thala"],
    "Sud": ["Gabès", "El Hamma", "Médenine", "Zarzis", "Djerba", "Gafsa", "Métlaoui", "Tozeur", "Nefta", "Tataouine", "Kébili"]
}

all_regions = []
for group in regions_data.values():
    all_regions.extend(group)

specialites = [
    "Médecine générale", "Cardiologie", "Dermatologie", "Pédiatrie", 
    "Ophtalmologie", "Gynécologie", "Neurologie", "Psychiatrie", "Dentaire", "Orthopédie"
]

noms = ["Trabelsi", "Ben Ali", "Ben Ammar", "Gharbi", "Cherif", "Bouazizi", "Jaziri", "Mabrouk", "Mansour", "Haddad", "Ayari", "Riahi", "Khlifi", "Zitouni", "Amri", "Baccouche", "Miled", "Sassi", "Touati", "Zouari", "Jemai", "Oueslati", "Tlili", "Ghannouchi", "Khemiri"]
prenoms = ["Ahmed", "Mohamed", "Youssef", "Sami", "Karim", "Walid", "Nizar", "Mehdi", "Ali", "Amine", "Amira", "Leïla", "Nadia", "Sarra", "Fatma", "Mouna", "Asma", "Rim", "Safa", "Yasmine", "Imen", "Salma", "Hichem", "Kamel", "Anis"]

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='gestion_des-rendez-vous5',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
        # Clear existing data just in case
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE personnel_de_sante")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Insert Meher Laibidi as #1
        cursor.execute("INSERT INTO personnel_de_sante (id_personnel, nom, prenom, specialite, disponibilite, region) VALUES (1, 'Labidi', 'Meher', 'Pediatre', 1, 'Ariana Ville')")
        
        # Insert 200 more doctors
        random.seed(123)
        for i in range(2, 202):
            nom = random.choice(noms)
            prenom = random.choice(prenoms)
            spec = random.choice(specialites)
            reg = random.choice(all_regions)
            cursor.execute("INSERT INTO personnel_de_sante (id_personnel, nom, prenom, specialite, disponibilite, region) VALUES (%s, %s, %s, %s, 1, %s)", (i, nom, prenom, spec, reg))
        
    conn.commit()
    print("Successfully inserted 201 doctors.")
except Exception as e:
    print("Error connecting or inserting:", e)
finally:
    if 'conn' in locals() and conn.open:
        conn.close()

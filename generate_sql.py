import random
import re

with open('database/gestion_des_rendez-vous 2.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# 1. Update the CREATE TABLE personnel_de_sante
if "`region` varchar(120) DEFAULT NULL" not in sql:
    sql = sql.replace(
        "`disponibilite` tinyint(1) NOT NULL DEFAULT 1\n) ENGINE=InnoDB",
        "`disponibilite` tinyint(1) NOT NULL DEFAULT 1,\n  `region` varchar(120) DEFAULT NULL\n) ENGINE=InnoDB"
    )

# 2. Extract everything before INSERT INTO `personnel_de_sante`
match = re.search(r"INSERT INTO `personnel_de_sante` \(`id_personnel`, `nom`, `prenom`, `specialite`, `disponibilite`\) VALUES", sql)
if match:
    head = sql[:match.end()]
    tail = sql[sql.find(";", match.end()):]

    # Generate 100 doctors + Meher Laibidi
    delegations = [
        "Tunis (Ville)", "Le Bardo", "Le Kram", "La Goulette", "Carthage", "Sidi Bou Saïd", 
        "La Marsa", "Sidi Hassine", "La Médina", "Bab El Bhar", "Bab Souika", "Sidi El Béchir", 
        "El Menzah", "Cité El Khadhra", "El Omrane", "El Omrane Supérieur", "Ettahrir", 
        "Djebel Djelloud", "El Ouardia", "El Kabaria", "Séjoumi", "Ezzouhour", "El Hrairia"
    ]

    specialites = [
        "Médecine générale", "Cardiologie", "Dermatologie", "Pédiatrie", 
        "Ophtalmologie", "Gynécologie", "Neurologie", "Psychiatrie", "Dentaire", "Orthopédie"
    ]

    noms = ["Trabelsi", "Ben Ali", "Ben Ammar", "Gharbi", "Cherif", "Bouazizi", "Jaziri", "Mabrouk", "Mansour", "Haddad", "Ayari", "Riahi", "Khlifi", "Zitouni", "Amri", "Baccouche", "Miled", "Sassi", "Touati", "Zouari"]
    prenoms = ["Ahmed", "Mohamed", "Youssef", "Sami", "Karim", "Walid", "Nizar", "Mehdi", "Ali", "Amine", "Amira", "Leïla", "Nadia", "Sarra", "Fatma", "Mouna", "Asma", "Rim", "Safa", "Yasmine"]

    # Update the INSERT INTO statement to include region
    head = head.replace("`disponibilite`)", "`disponibilite`, `region`)")

    values = []
    values.append("\n(1, 'Labidi', 'Meher', 'Pediatre', 1, 'Tunis (Ville)')")

    random.seed(42) # For reproducibility
    for i in range(2, 102):
        nom = random.choice(noms)
        prenom = random.choice(prenoms)
        spec = random.choice(specialites)
        reg = random.choice(delegations)
        values.append(f"\n({i}, '{nom}', '{prenom}', '{spec}', 1, '{reg}')")

    new_sql = head + ",".join(values) + tail

    with open('database/gestion_des_rendez-vous 2.sql', 'w', encoding='utf-8') as f:
        f.write(new_sql)

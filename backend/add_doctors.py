import sys
from app import app, db, PersonnelDeSante

doctors_data = [
    {"nom": "Ben Salah", "prenom": "Amira", "specialite": "Médecine générale", "type_personnel": "medecin"},
    {"nom": "Trabelsi", "prenom": "Karim", "specialite": "Cardiologie", "type_personnel": "medecin"},
    {"nom": "Mansour", "prenom": "Leïla", "specialite": "Dermatologie", "type_personnel": "medecin"},
    {"nom": "Haddad", "prenom": "Youssef", "specialite": "Pédiatrie", "type_personnel": "medecin"},
    {"nom": "Gharbi", "prenom": "Sami", "specialite": "Dentaire", "type_personnel": "medecin"},
    {"nom": "Cherif", "prenom": "Nadia", "specialite": "Ophtalmologie", "type_personnel": "medecin"}
]

with app.app_context():
    for doc in doctors_data:
        existing = PersonnelDeSante.query.filter_by(nom=doc["nom"], prenom=doc["prenom"]).first()
        if not existing:
            new_doc = PersonnelDeSante(
                nom=doc["nom"],
                prenom=doc["prenom"],
                specialite=doc["specialite"],
                type_personnel=doc["type_personnel"]
            )
            db.session.add(new_doc)
    
    db.session.commit()
    print("Docteurs ajoutés avec succès.")

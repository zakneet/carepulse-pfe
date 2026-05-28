import sys
from app import app, db, PersonnelDeSante

doctors_data = [
    {"nom": "Ben Salah", "prenom": "Amira", "specialite": "Médecine générale"},
    {"nom": "Trabelsi", "prenom": "Karim", "specialite": "Cardiologie"},
    {"nom": "Mansour", "prenom": "Leïla", "specialite": "Dermatologie"},
    {"nom": "Haddad", "prenom": "Youssef", "specialite": "Pédiatrie"},
    {"nom": "Gharbi", "prenom": "Sami", "specialite": "Dentaire"},
    {"nom": "Cherif", "prenom": "Nadia", "specialite": "Ophtalmologie"}
]

with app.app_context():
    for doc in doctors_data:
        existing = PersonnelDeSante.query.filter_by(nom=doc["nom"], prenom=doc["prenom"]).first()
        if not existing:
            new_doc = PersonnelDeSante(
                nom=doc["nom"],
                prenom=doc["prenom"],
                specialite=doc["specialite"],
                disponibilite=True
            )
            db.session.add(new_doc)
    
    db.session.commit()
    print("Docteurs ajoutés avec succès.")

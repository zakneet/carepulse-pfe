from app import app, db, User, Planning, Rdv
from datetime import date, time

with app.app_context():
    # Créer les tables
    db.create_all()
    print('✅ Tables créées')
    
    # Créer un patient
    patient = User(nom='Dupont', prenom='Alice', email='alice@test.com', telephone='0123456789', statut=1)
    db.session.add(patient)
    db.session.commit()
    print(f'✅ Patient créé: ID {patient.id}')
    
    # Créer un médecin
    doctor = User(nom='Martin', prenom='Jean', specialite='Cardiologie', disponibilite='09:00-17:00', statut=2)
    db.session.add(doctor)
    db.session.commit()
    print(f'✅ Médecin créé: ID {doctor.id}')
    
    # Créer un planning avec FK vers le médecin
    planning = Planning(
        date=date(2026, 4, 15),
        heure_debut=time(9, 0),
        heure_fin=time(17, 0),
        duree_creneau=30,
        idPersonnel=doctor.id
    )
    db.session.add(planning)
    db.session.commit()
    print(f'✅ Planning créé: ID {planning.idPlanning} pour médecin {doctor.id}')
    
    # Créer un RDV avec FK vers patient et médecin
    rdv = Rdv(
        idPatient=patient.id,
        idPersonnel=doctor.id,
        dateRDV=date(2026, 4, 15),
        heureDebut=time(10, 0),
        heureFin=time(10, 30),
        statut='consultation'
    )
    db.session.add(rdv)
    db.session.commit()
    print(f'✅ RDV créé: ID {rdv.idRdv} - Patient {patient.id} avec Médecin {doctor.id}')
    
    # Vérifier les relations
    rdv_loaded = Rdv.query.get(rdv.idRdv)
    print(f'\n📋 Vérification des relations:')
    print(f'   RDV Patient: {rdv_loaded.patient.nom} {rdv_loaded.patient.prenom}')
    print(f'   RDV Médecin: {rdv_loaded.personnel.nom} {rdv_loaded.personnel.prenom}')
    print(f'   RDV Statut: {rdv_loaded.statut}')
    
    # Afficher les tables
    print(f'\n📊 Vérification des tables:')
    users = User.query.all()
    print(f'   Users: {len(users)} lignes')
    plannings = Planning.query.all()
    print(f'   Planning: {len(plannings)} lignes')
    rdvs = Rdv.query.all()
    print(f'   RDV: {len(rdvs)} lignes')
    
    print(f'\n✅ BACKEND PRÊT - Sans table access_codes, clés étrangères OK!')

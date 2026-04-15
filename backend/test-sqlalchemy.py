#!/usr/bin/env python
"""
Script de test pour vérifier la migration SQLAlchemy
"""

from app import app, db, User, RDV, AccessCode
from datetime import date, time

def test_database():
    """Test basic CRUD operations"""
    with app.app_context():
        print("=" * 60)
        print("TEST: Migration SQLAlchemy")
        print("=" * 60)
        
        # 1. Vérifier les tables
        tables = db.inspect(db.engine).get_table_names()
        print(f"\n✅ Tables créées: {tables}")
        
        # 2. Créer un utilisateur de test
        print("\n--- Test Create User ---")
        test_user = User(
            nom="Dupont",
            prenom="Jean",
            email="test@example.com",
            password="test123",
            role="patient",
            specialite=None
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"✅ Utilisateur créé: {test_user.nom} {test_user.prenom} (ID: {test_user.id})")
        
        # 3. Créer un personnel médical
        print("\n--- Test Create Medical Staff ---")
        doc = User(
            nom="Docteur",
            prenom="Martin",
            email="doctor@example.com",
            password="doc123",
            role="medical_staff",
            specialite="Cardiologie"
        )
        db.session.add(doc)
        db.session.commit()
        print(f"✅ Personnel créé: {doc.nom} {doc.prenom} (ID: {doc.id})")
        
        # 4. Créer un RDV
        print("\n--- Test Create RDV ---")
        rdv = RDV(
            idPatient=test_user.id,
            idPersonnel=doc.id,
            dateRDV=date(2026, 4, 15),
            heureDebut=time(14, 30),
            heureFin=time(15, 0),
            motifConsultation="Consultation cardiaque",
            statut="Confirme"
        )
        db.session.add(rdv)
        db.session.commit()
        print(f"✅ RDV créé: {rdv.dateRDV} à {rdv.heureDebut} (ID: {rdv.idRDV})")
        
        # 5. Récupérer et afficher les données
        print("\n--- Test Read Data ---")
        all_users = User.query.all()
        print(f"✅ Total utilisateurs: {len(all_users)}")
        for u in all_users[:5]:
            print(f"  - {u.nom} {u.prenom} ({u.role})")
        
        all_rdvs = RDV.query.all()
        print(f"✅ Total RDVs: {len(all_rdvs)}")
        for r in all_rdvs[:5]:
            print(f"  - {r.dateRDV} {r.heureDebut}: {r.motifConsultation}")
        
        # 6. Créer un code d'accès
        print("\n--- Test Access Code ---")
        import hashlib
        code_hash = hashlib.sha256("TEST123".encode()).hexdigest()
        access_code = AccessCode(
            code_hash=code_hash,
            user_type="medical_staff",
            description="Code de test"
        )
        db.session.add(access_code)
        db.session.commit()
        print(f"✅ Code d'accès créé (ID: {access_code.id})")
        
        # 7. Tester les relations
        print("\n--- Test Relations ---")
        rdv = RDV.query.first()
        if rdv and rdv.patient:
            print(f"✅ Patient du RDV: {rdv.patient.nom} {rdv.patient.prenom}")
        if rdv and rdv.personnel:
            print(f"✅ Personnel du RDV: {rdv.personnel.nom} {rdv.personnel.prenom}")
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("=" * 60)

if __name__ == "__main__":
    test_database()

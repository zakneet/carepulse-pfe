#!/usr/bin/env python3
from app import app

c = app.test_client()

# Test du planning
print("=== TEST 1: Recupérer le planning ===")
r = c.get('/medical-staff/planning?date=2026-04-02&idPersonnel=12')
print('Status:', r.status_code)
data = r.get_json()
print('Response keys:', list(data.keys()))

if 'error' in data:
    print('Error:', data['error'])
else:
    rdvs = data.get('todayPlanning', [])
    print('RDVs trouves:', len(rdvs))
    
    if rdvs:
        print("\nRDV avant decalage:")
        for rdv in rdvs:
            print(f"  ID {rdv.get('id')}: {rdv.get('heureDebut')} - {rdv.get('motifConsultation')}")

        # Decaler le premier RDV
        print("\n=== TEST 2: Decaler le premier RDV ===")
        rdv_id = rdvs[0]['id']
        print(f"Decalage du RDV {rdv_id}...")
        
        payload = {
            'heureDebut': '16:00:00',
            'heureFin': '16:30:00',
            'statut': 'Décalé (urgence patient)',
            'motifConsultation': 'Décalé - Consultation test'
        }
        r = c.put(f'/update_rdv/{rdv_id}', json=payload)
        print(f'Response: {r.status_code}')
        
        # Verifier la persistance
        print("\n=== TEST 3: Verifier la persistance ===")
        r = c.get('/medical-staff/planning?date=2026-04-02&idPersonnel=12')
        data = r.get_json()
        rdvs_after = data.get('todayPlanning', [])
        
        for rdv in rdvs_after:
            if rdv['id'] == rdv_id:
                print(f"RDV {rdv['id']} APRES decalage: {rdv['heureDebut']} | {rdv['statut']}")
                if rdv['heureDebut'] == '16:00:00' and 'Décalé' in rdv['statut']:
                    print("✅ SUCCES: Le decalage a ete persiste en base de donnees!")
                else:
                    print("❌ ECHEC: Le decalage n'a pas ete persiste")

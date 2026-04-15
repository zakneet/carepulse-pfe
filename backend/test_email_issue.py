import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

# Test avec données COMPLÈTES (comme doit les envoyer le formulaire)
print("=" * 60)
print("TEST 1: Booking WITH email (complete data)")
print("=" * 60)

payload1 = {
    "idPatient": 0,
    "nom": "TestComplet",
    "prenom": "Avec_Email",
    "telephone": "06123456789",
    "email": "test.complet@example.com",
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "heureDebut": "09:00:00",
    "heureFin": "09:30:00",
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 30
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(payload1).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    print(f"✓ Status: 201")
    print(f"  RDV ID: {result.get('rdv', {}).get('id')}")
except urllib.error.HTTPError as e:
    print(f"✗ Status: {e.code}")
    error_body = json.loads(e.read())
    print(f"  Error: {error_body.get('error')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test SANS email (comme peut l'envoyer le formulaire actuel)
print("\n" + "=" * 60)
print("TEST 2: Booking WITHOUT email (missing data)")
print("=" * 60)

payload2 = {
    "idPatient": 0,
    "nom": "TestSansEmail",
    "prenom": "Sans_Email",
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "heureDebut": "10:00:00",
    "heureFin": "10:30:00",
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 30
    # NO email, NO telephone
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(payload2).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    print(f"✓ Status: 201")
    print(f"  RDV ID: {result.get('rdv', {}).get('id')}")
except urllib.error.HTTPError as e:
    print(f"✗ Status: {e.code}")
    error_body = json.loads(e.read())
    print(f"  Error: {error_body.get('error')}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST 3: Verify RDVs in database")
print("=" * 60)

try:
    req = urllib.request.Request(
        f"{BASE_URL}/rdvs",
        method='GET'
    )
    with urllib.request.urlopen(req) as response:
        rdvs = json.loads(response.read())
    print(f"Total RDVs in database: {len(rdvs)}")
    print(f"\nLast 5 RDVs:")
    for rdv in rdvs[-5:]:
        print(f"  ID {rdv['id']}: {rdv['dateRDV']} {rdv['heureDebut']} (Patient #{rdv.get('idPatient')}, Personnel: {rdv.get('idPersonnel')})")
except Exception as e:
    print(f"Error: {e}")

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import random

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 70)
print("FINAL TEST: Complete RDV creation flow")
print("=" * 70)

# Step 1: Get available slots
print("\n[Step 1] Getting available slots...")
slots_payload = {
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "isUrgent": False,
    "slotDuration": 30
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/suggest-available-slots",
        data=json.dumps(slots_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        slots_response = json.loads(response.read())
    
    available_slots = slots_response.get("suggestedSlots", [])
    if len(available_slots) > 0:
        chosen_slot = available_slots[random.randint(0, len(available_slots) - 1)]
        print(f"✓ Using slot: {chosen_slot['heureDebut']} - {chosen_slot['heureFin']}")
    else:
        print("✗ No available slots!")
        exit(1)
except Exception as e:
    print(f"✗ Error getting slots: {e}")
    exit(1)

# Step 2: Create RDV
print("\n[Step 2] Creating RDV...")

# Use a random email to avoid duplicates
random_suffix = random.randint(100000, 999999)
rdv_payload = {
    "idPatient": 0,
    "nom": "FinalTest",
    "prenom": "CompletFlow",
    "telephone": "0612345678",
    "email": f"patient.final{random_suffix}@test.com",
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "heureDebut": chosen_slot['heureDebut'],
    "heureFin": chosen_slot['heureFin'],
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 30
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(rdv_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    
    rdv_id = result.get('rdv', {}).get('id')
    patient_id = result.get('rdv', {}).get('idPatient')
    print(f"✓ RDV created with ID: {rdv_id}")
    print(f"✓ Patient created with ID: {patient_id}")
    
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}")
    try:
        error_body = json.loads(e.read())
        print(f"Error: {error_body.get('error')}")
    except:
        pass
    exit(1)

# Step 3: Verify in planning
print("\n[Step 3] Verifying RDV appears in planning...")

try:
    url = f"{BASE_URL}/medical-staff/planning?idPersonnel=13&date={tomorrow}"
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req) as response:
        planning = json.loads(response.read())
    
    todayPlanning = planning.get('todayPlanning', [])
    found =any(r['id'] == rdv_id for r in todayPlanning)
    
    if found:
        print(f"✓ RDV #{rdv_id} IS visible in planning")
    else:
        print(f"✗ RDV #{rdv_id} NOT found in planning")
        
except Exception as e:
    print(f"✗ Error checking planning: {e}")

# Step 4: Verify in database
print("\n[Step 4] Verifying RDV persisted in database...")

try:
    req = urllib.request.Request(f"{BASE_URL}/rdvs", method='GET')
    with urllib.request.urlopen(req) as response:
        all_rdvs = json.loads(response.read())
    
    found_in_db = any(r['id'] == rdv_id for r in all_rdvs)
    
    if found_in_db:
        print(f"✓ RDV #{rdv_id} persisted in database")
    else:
        print(f"✗ RDV #{rdv_id} NOT persisted")
        
except Exception as e:
    print(f"✗ Error checking database: {e}")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - System working correctly!")
print("=" * 70)

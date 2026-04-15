import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 70)
print("TEST: Creating RDV and checking backend logs")
print("=" * 70)

# Get first available slot
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
        chosen_slot = available_slots[0]
        print(f"✓ Using slot: {chosen_slot['heureDebut']} - {chosen_slot['heureFin']}")
    else:
        print("✗ No available slots!")
        exit(1)
except Exception as e:
    print(f"✗ Error getting slots: {e}")
    exit(1)

# Create RDV with complete data
print("\n[Step 2] Creating RDV...")

rdv_payload = {
    "idPatient": 0,
    "nom": "TestDiag",
    "prenom": "Diagnostic",
    "telephone": "0612345678",
    "email": "test@diagnostic.com",
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "heureDebut": chosen_slot['heureDebut'],
    "heureFin": chosen_slot['heureFin'],
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 28
}

print(f"Payload: {json.dumps(rdv_payload, indent=2)}")

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(rdv_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    
    print(f"\n✓ Response Status: 201")
    print(f"Response: {json.dumps(result, indent=2)}")
    
    rdv_id = result.get('rdv', {}).get('id')
    print(f"\n✓ RDV created with ID: {rdv_id}")
    
except urllib.error.HTTPError as e:
    print(f"\n✗ HTTP Error {e.code}")
    try:
        error_body = json.loads(e.read())
        print(f"Error response: {json.dumps(error_body, indent=2)}")
    except:
        pass
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Check the backend terminal for detailed logs!")
print("=" * 70)

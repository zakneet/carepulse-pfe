import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import random

def Number(val):
    """Convert to number like JavaScript"""
    if val is None:
        return 0
    try:
        return float(val)
    except:
        return 0

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 70)
print("END-TO-END TEST: Simulating RDV Form Submission")
print("=" * 70)

# Step 0: Get available slots first
print("\n[0] Getting available slots...")

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
        # Pick a random available slot
        chosen_slot = available_slots[random.randint(0, len(available_slots) - 1)]
        print(f"✓ Found {len(available_slots)} available slots")
        print(f"✓ Using slot: {chosen_slot['heureDebut']} - {chosen_slot['heureFin']}")
    else:
        print("✗ No available slots!")
        exit(1)
except Exception as e:
    print(f"✗ Error getting slots: {e}")
    exit(1)

# Step 1: Create RDV (simulating form submittal)
print("\n[1] Creating RDV (form submittal simulation)...")

rdv_payload = {
    "idPatient": 0,
    "nom": "FormulaireFront",
    "prenom": "E2E_Test",
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "heureDebut": chosen_slot['heureDebut'],
    "heureFin": chosen_slot['heureFin'],
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 25
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
        addrdv_response = json.loads(response.read())
    
    print(f"✓ RDV Created with status 201")
    rdv_data = addrdv_response.get('rdv', {})
    print(f"Response RDV data: {json.dumps(rdv_data, indent=2)}")
    
    # Extract ID like frontend does
    createdId = Number(rdv_data.get('id') or rdv_data.get('idRdv') or rdv_data.get('idRDV'))
    createdId = int(createdId)
    print(f"Extracted ID: {createdId}")
    
except urllib.error.HTTPError as e:
    print(f"✗ Status: {e.code}")
    error_body = json.loads(e.read())
    print(f"Error: {error_body.get('error')}")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Fetch planning like frontend does
print(f"\n[2] Fetching medical staff planning (verifying RDV appears)...")
print(f"Parameters: idPersonnel={rdv_payload['idPersonnel']}, date={rdv_payload['dateRDV']}")

try:
    url = f"{BASE_URL}/medical-staff/planning?idPersonnel={rdv_payload['idPersonnel']}&date={rdv_payload['dateRDV']}"
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req) as response:
        planning_response = json.loads(response.read())
    
    print(f"✓ Planning fetched")
    todayPlanning = planning_response.get('todayPlanning', [])
    print(f"  Found {len(todayPlanning)} appointments for {tomorrow}")
    
    # Check if our RDV appears
    foundInPlanning = any(Number(item.get('id') or item.get('idRDV') or item.get('idRdv')) == createdId for item in todayPlanning)
    
    if foundInPlanning:
        print(f"✓ SUCCESS: RDV #{createdId} is visible in planning!")
    else:
        print(f"✗ ERROR: RDV #{createdId} NOT found in planning!")
        print(f"\nAll RDVs in planning:")
        for rdv in todayPlanning:
            rdv_id = Number(rdv.get('id') or rdv.get('idRDV') or rdv.get('idRdv'))
            print(f"  ID {rdv_id}: {rdv.get('heureDebut')} - {rdv.get('heureFin')}")
            
except urllib.error.HTTPError as e:
    print(f"✗ Status: {e.code}")
    error_body = json.loads(e.read())
    print(f"Error: {error_body.get('error')}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()


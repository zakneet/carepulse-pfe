#!/usr/bin/env python
"""Test script to verify booking conflict detection using urllib."""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# Test data
test_patient_name = f"Patient_Test_{int(datetime.now().timestamp())}"
test_patient_first = "Test"
test_doctor_id = 13  # Using doctor Martin Docteur
test_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 60)
print("BOOKING CONFLICT DETECTION TEST")
print("=" * 60)

# Step 1: Get available slots
print("\n1. Getting available slots...")
slots_payload = {
    "idPersonnel": test_doctor_id,
    "dateRDV": test_date,
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
    
    print(f"Status: 200")
    available_slots = slots_response.get("suggestedSlots", [])
    print(f"Available slots: {len(available_slots)}")
except Exception as e:
    print(f"ERROR getting slots: {e}")
    exit(1)

if not available_slots:
    print("ERROR: No available slots found. Cannot proceed with test.")
    exit(1)

# Use first two available slots
slot1 = available_slots[0]
slot2 = available_slots[1] if len(available_slots) > 1 else available_slots[0]

print(f"Slot 1: {slot1['heureDebut']} - {slot1['heureFin']}")
print(f"Slot 2: {slot2['heureDebut']} - {slot2['heureFin']}")

# Step 2: Book the first slot
print("\n2. Booking first appointment (should succeed)...")
booking1_payload = {
    "idPatient": 0,
    "nom": test_patient_name,
    "prenom": test_patient_first,
    "idPersonnel": test_doctor_id,
    "dateRDV": test_date,
    "heureDebut": slot1['heureDebut'],
    "heureFin": slot1['heureFin'],
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 30
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(booking1_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        booking1_response = json.loads(response.read())
    
    print(f"Status: 201")
    print(f"Response: {json.dumps(booking1_response, indent=2)}")
    rdv_id = booking1_response.get("rdv", {}).get("id")
    print(f"✓ First appointment created with ID: {rdv_id}")
except urllib.error.HTTPError as e:
    print(f"ERROR: First booking failed with status {e.code}")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# Step 3: Try to book the same slot (should fail with 409)
print("\n3. Attempting to book the same slot (should FAIL with 409)...")
booking2_payload = {
    "idPatient": 0,
    "nom": f"{test_patient_name}_2",
    "prenom": test_patient_first,
    "idPersonnel": test_doctor_id,
    "dateRDV": test_date,
    "heureDebut": slot1['heureDebut'],
    "heureFin": slot1['heureFin'],
    "motifConsultation": "consultation",
    "statut": "consultation",
    "agePatient": 30
}

try:
    req = urllib.request.Request(
        f"{BASE_URL}/add_rdv",
        data=json.dumps(booking2_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        booking2_response = json.loads(response.read())
    print(f"Status: 201 (UNEXPECTED - should have been 409)")
    print(f"✗ ERROR: Booking was allowed when it should have been rejected!")
except urllib.error.HTTPError as e:
    if e.code == 409:
        response_data = json.loads(e.read())
        print(f"Status: 409")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        print("✓ CONFLICT DETECTED! Status 409 returned as expected")
        conflict_info = response_data.get("conflictingAppointment")
        if conflict_info:
            print(f"  Conflicting appointment: {conflict_info.get('heureDebut')} - {conflict_info.get('heureFin')}")
            print(f"  With patient: {conflict_info.get('patientPrenom')} {conflict_info.get('patientNom')}")
    else:
        print(f"Status: {e.code}")
        print(f"✗ ERROR: Expected 409 but got {e.code}")
except Exception as e:
    print(f"ERROR: {e}")

# Step 4: Book a different slot (should succeed)
print("\n4. Booking different time slot (should succeed)...")
if slot1['heureDebut'] != slot2['heureDebut']:
    booking3_payload = {
        "idPatient": 0,
        "nom": f"{test_patient_name}_3",
        "prenom": test_patient_first,
        "idPersonnel": test_doctor_id,
        "dateRDV": test_date,
        "heureDebut": slot2['heureDebut'],
        "heureFin": slot2['heureFin'],
        "motifConsultation": "consultation",
        "statut": "consultation",
        "agePatient": 30
    }

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/add_rdv",
            data=json.dumps(booking3_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            booking3_response = json.loads(response.read())
        
        print(f"Status: 201")
        rdv_id_2 = booking3_response.get("rdv", {}).get("id")
        print(f"✓ Second appointment created with ID: {rdv_id_2}")
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}")
        print(f"✗ ERROR: Could not book different slot")
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("NOTE: Only one unique slot available for this test date")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

#!/usr/bin/env python
"""Test script to verify booking conflict detection."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# Test data
test_patient_name = f"Patient_Test_{datetime.now().timestamp()}"
test_patient_first = "Test"
test_doctor_id = 2  # Assuming doctor with ID 2 exists
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

slots_response = requests.post(f"{BASE_URL}/suggest-available-slots", json=slots_payload)
print(f"Status: {slots_response.status_code}")
available_slots = slots_response.json().get("suggestedSlots", [])
print(f"Available slots: {len(available_slots)}")

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

booking1_response = requests.post(f"{BASE_URL}/add_rdv", json=booking1_payload)
print(f"Status: {booking1_response.status_code}")
print(f"Response: {json.dumps(booking1_response.json(), indent=2)}")

if booking1_response.status_code != 201:
    print("ERROR: First booking failed. Cannot proceed with conflict test.")
    exit(1)

rdv_id = booking1_response.json().get("rdv", {}).get("id")
print(f"✓ First appointment created with ID: {rdv_id}")

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

booking2_response = requests.post(f"{BASE_URL}/add_rdv", json=booking2_payload)
print(f"Status: {booking2_response.status_code}")
print(f"Response: {json.dumps(booking2_response.json(), indent=2)}")

if booking2_response.status_code == 409:
    print("✓ CONFLICT DETECTED! Status 409 returned as expected")
    conflict_info = booking2_response.json().get("conflictingAppointment")
    if conflict_info:
        print(f"  Conflicting appointment: {conflict_info.get('heureDebut')} - {conflict_info.get('heureFin')}")
        print(f"  With patient: {conflict_info.get('patientPrenom')} {conflict_info.get('patientNom')}")
else:
    print(f"✗ ERROR: Expected 409 but got {booking2_response.status_code}")

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

    booking3_response = requests.post(f"{BASE_URL}/add_rdv", json=booking3_payload)
    print(f"Status: {booking3_response.status_code}")
    print(f"Response: {json.dumps(booking3_response.json(), indent=2)}")

    if booking3_response.status_code == 201:
        rdv_id_2 = booking3_response.json().get("rdv", {}).get("id")
        print(f"✓ Second appointment created with ID: {rdv_id_2}")
    else:
        print(f"✗ ERROR: Could not book different slot. Status: {booking3_response.status_code}")
else:
    print("NOTE: Only one unique slot available for this test date")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

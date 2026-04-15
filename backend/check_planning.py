import json
import urllib.request
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 70)
print("VERIFICATION: Check if RDV #109 appears in planning")
print("=" * 70)

try:
    url = f"{BASE_URL}/medical-staff/planning?idPersonnel=13&date={tomorrow}"
    request = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read())
    
    todayPlanning = result.get('todayPlanning', [])
    print(f"\n✓ Status: 200")
    print(f"Found {len(todayPlanning)} appointments for {tomorrow}")
    
    rdv_ids = [r['id'] for r in todayPlanning]
    print(f"\nRDV IDs in planning: {rdv_ids}")
    
    if 109 in rdv_ids:
        print("✓ RDV #109 IS visible in planning!")
        # Find it and display details
        for rdv in todayPlanning:
            if rdv['id'] == 109:
                print(f"\nDetails of RDV #109:")
                print(f"  Time: {rdv['heureDebut']} - {rdv['heureFin']}")
                print(f"  Patient: {rdv.get('patientPrenom')} {rdv.get('patientNom')}")
                print(f"  Motif: {rdv.get('motifConsultation')}")
    else:
        print("✗ RDV #109 NOT found in planning")
        print(f"\nAll RDVs:")
        for rdv in todayPlanning:
            print(f"  ID {rdv['id']}: {rdv['heureDebut']} - {rdv['heureFin']}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

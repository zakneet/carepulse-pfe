import json
import urllib.request

BASE_URL = "http://127.0.0.1:5000"

# Get medical staff
print("Getting list of medical staff...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/medical-staff",
        method='GET'
    )
    with urllib.request.urlopen(req) as response:
        staff_list = json.loads(response.read())
    
    print(f"Found {len(staff_list)} medical staff members:")
    for staff in staff_list:
        print(f"  ID {staff['id']}: Dr {staff['prenom']} {staff['nom']} ({staff.get('specialite', 'N/A')})")
    
    if staff_list:
        first_doctor_id = staff_list[0]['id']
        print(f"\nUsing doctor ID: {first_doctor_id}")
except Exception as e:
    print(f"Error: {e}")

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

from app import app, db

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

print("=" * 60)
print("TEST: Getting medical staff planning")
print("=" * 60)
print(f"Date: {tomorrow}")

with app.app_context():
    with db.engine.connect() as conn:
        personnel_row = conn.exec_driver_sql(
            """
            SELECT id_personnel
            FROM personnel_de_sante
            WHERE type_personnel IN ('medecin', 'secretaire')
            ORDER BY id_personnel ASC
            LIMIT 1
            """
        ).mappings().first()

personnel_id = personnel_row["id_personnel"] if personnel_row else 0

try:
    url = f"{BASE_URL}/medical-staff/planning?idPersonnel={personnel_id}&date={tomorrow}"
    print(f"URL: {url}")
    request = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read())
    
    print(f"✓ Status: 200")
    print(f"Personnel ID: {result.get('idPersonnel')}")
    print(f"Date: {result.get('date')}")
    print(f"Today's appointments: {len(result.get('todayPlanning', []))}")
    
    print(f"\nRDVs for {tomorrow}:")
    for rdv in result.get('todayPlanning', []):
        print(f"  ID {rdv['id']}: {rdv['heureDebut']} - {rdv['heureFin']} (Patient #{rdv.get('idPatient')})")
    
except urllib.error.HTTPError as e:
    print(f"✗ Status: {e.code}")
    try:
        error_body = json.loads(e.read())
        print(f"  Error: {json.dumps(error_body, indent=2)}")
    except:
        pass
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

payload = {
    "idPersonnel": 13,
    "dateRDV": tomorrow,
    "isUrgent": False,
    "slotDuration": 30
}

print(f"Testing with date: {tomorrow}")
print(f"Payload: {json.dumps(payload)}")

try:
    req = urllib.request.Request(
        f"{BASE_URL}/suggest-available-slots",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    slots = result.get('suggestedSlots', [])
    print(f"Slots found: {len(slots)}")
    for i, s in enumerate(slots[:5]):
        print(f"  {i+1}. {s['heureDebut']} - {s['heureFin']}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}")
    try:
        error_body = json.loads(e.read())
        print(f"Error response: {json.dumps(error_body, indent=2)}")
    except:
        print(f"Error body could not be parsed")
except Exception as e:
    print(f"Error: {e}")

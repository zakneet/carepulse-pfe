import urllib.request
import urllib.error

url = 'http://127.0.0.1:5000/medical-staff/patients?idPersonnel=1'
print('Calling:', url)
req = urllib.request.Request(url, headers={'Accept': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.getcode()
        body = resp.read().decode('utf-8')
        print('Status:', status)
        print('Body:', body)
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    try:
        print('Body:', e.read().decode('utf-8'))
    except Exception:
        pass
except Exception as e:
    print('Error:', str(e))

import urllib.request
import json

r = urllib.request.urlopen('http://127.0.0.1:5000/rdvs')
rdvs = json.loads(r.read())

print(f'✓ Total RDVs en base de données: {len(rdvs)}')
print(f'\nDerniers 5 RDVs créés:')
for rdv in rdvs[-5:]:
    print(f'  ID {rdv["id"]}: {rdv["dateRDV"]} {rdv["heureDebut"]} (Patient #{rdv.get("idPatient")})')

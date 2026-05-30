from app import app, db
from datetime import datetime, timedelta

with app.app_context():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    personnel_id = 1
    print(f"Listing RDVs for personnel {personnel_id} on {tomorrow}")
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT idRDV, idPatient, idPersonnel, dateRDV, heureDebut, heureFin, motifConsultation FROM rdv WHERE idPersonnel=%s AND dateRDV=%s ORDER BY heureDebut",
            (personnel_id, tomorrow),
        ).mappings().all()
    print(f"Found {len(rows)} rows")
    for r in rows:
        print(dict(r))

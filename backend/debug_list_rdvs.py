from app import db, app
from sqlalchemy import text

def list_rdvs(personnel_id, date):
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT idRDV, idPatient, idPersonnel, dateRDV, heureDebut, heureFin, motifConsultation, statut FROM rdv WHERE idPersonnel=%s AND dateRDV=%s ORDER BY heureDebut",
            (personnel_id, date),
        ).mappings().all()
    for r in rows:
        print(dict(r))

if __name__ == '__main__':
    with app.app_context():
        list_rdvs(1, '2026-05-22')

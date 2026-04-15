#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta

from app import app, db, Rdv, User


def resolve_user_role_column():
    if hasattr(User, "statut"):
        return "statut"
    if hasattr(User, "role"):
        return "role"
    return None


def find_doctor_and_patient():
    role_column = resolve_user_role_column()

    if role_column == "statut":
        doctor = User.query.filter(User.statut == 2).order_by(User.id.asc()).first()
        patient = User.query.filter(User.statut == 1).order_by(User.id.asc()).first()
        return doctor, patient

    if role_column == "role":
        doctor = User.query.filter(User.role == "medical_staff").order_by(User.id.asc()).first()
        patient = User.query.filter(User.role == "patient").order_by(User.id.asc()).first()
        return doctor, patient

    return None, None


def parse_args():
    parser = argparse.ArgumentParser(description="Create deterministic RDV test data.")
    parser.add_argument(
        "--date",
        dest="date_value",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format. Defaults to today.",
    )
    return parser.parse_args()


def resolve_rdv_id(rdv):
    return getattr(rdv, "idRDV", getattr(rdv, "idRdv", getattr(rdv, "id", None)))


def minutes_to_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}:00"


with app.app_context():
    args = parse_args()
    test_date = datetime.strptime(args.date_value, "%Y-%m-%d").date()

    doctor, patient = find_doctor_and_patient()
    if not doctor or not patient:
        print("ERROR: doctor or patient not found")
        raise SystemExit(1)

    # Remove only previously generated test appointments for this doctor/day.
    old_rdvs = (
        Rdv.query.filter(
            Rdv.dateRDV == test_date,
            Rdv.idPersonnel == doctor.id,
            Rdv.motifConsultation.like("%TEST%"),
        )
        .order_by(Rdv.heureDebut.asc())
        .all()
    )
    for rdv in old_rdvs:
        db.session.delete(rdv)
    db.session.commit()

    # Four consecutive appointments make it easy to verify that only one RDV changes.
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    # Dashboard grid shows slots from 08:00 to 18:00.
    # Keep 4 x 30-minute appointments fully inside this range.
    base_minutes = max(8 * 60, ((current_minutes - 30) // 30) * 30)
    base_minutes = min(base_minutes, 16 * 60)

    times = []
    for index in range(4):
        start_minutes = base_minutes + (index * 30)
        end_minutes = start_minutes + 30
        times.append((minutes_to_time(start_minutes), minutes_to_time(end_minutes), f"TEST - Consultation {index + 1}"))

    created_ids = []
    for start_time, end_time, motif in times:
        rdv = Rdv(
            idPatient=patient.id,
            idPersonnel=doctor.id,
            dateRDV=test_date,
            heureDebut=start_time,
            heureFin=end_time,
            motifConsultation=motif,
            statut="consultation",
        )
        db.session.add(rdv)
        db.session.flush()
        created_ids.append(resolve_rdv_id(rdv))

    db.session.commit()

    print("OK: RDV de test créés")
    print(f"Doctor ID: {doctor.id}, Patient ID: {patient.id}")
    print(f"Date: {test_date.isoformat()}")
    print("\nRDV créés:")
    for index, (start, end, motif) in enumerate(times):
        print(f"  ID {created_ids[index]}: {start} -> {end} ({motif})")

    print("\nPour tester l'urgence patient:")
    print("- ouvre le planning du jour")
    print("- clique un seul RDV test")
    print("- puis clique sur 'Urgence Patient present au cabinet'")
    print("- seul le RDV sélectionné doit être décalé")

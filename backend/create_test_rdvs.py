#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta

from app import app, db, Rdv


def find_doctor_and_patient():
    with db.engine.connect() as conn:
        doctor = conn.exec_driver_sql(
            """
            SELECT id_personnel AS id, nom, prenom
            FROM personnel_de_sante
            ORDER BY id_personnel ASC
            LIMIT 1
            """
        ).mappings().first()

        patient = conn.exec_driver_sql(
            """
            SELECT id_patient AS id, nom, prenom
            FROM patient
            ORDER BY id_patient ASC
            LIMIT 1
            """
        ).mappings().first()

    return doctor, patient


def find_doctor_and_patient_by_id(personnel_id=None):
    with db.engine.connect() as conn:
        if personnel_id:
            doctor = conn.exec_driver_sql(
                """
                SELECT id_personnel AS id, nom, prenom
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (personnel_id,)
            ).mappings().first()
        else:
            doctor = None

        patient = conn.exec_driver_sql(
            """
            SELECT id_patient AS id, nom, prenom
            FROM patient
            ORDER BY id_patient ASC
            LIMIT 1
            """
        ).mappings().first()

    return doctor, patient


def parse_args():
    parser = argparse.ArgumentParser(description="Create deterministic RDV test data.")
    parser.add_argument(
        "--date",
        dest="date_value",
        default=(datetime.now()).strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--count",
        dest="count",
        type=int,
        default=4,
        help="Number of test appointments to create (default: 4)",
    )
    parser.add_argument(
        "--duration",
        dest="duration",
        type=int,
        default=30,
        help="Duration of each test appointment in minutes (default: 30)",
    )
    parser.add_argument(
        "--start",
        dest="start_time",
        default=None,
        help="Optional start time for the first slot (HH:MM). If omitted, a context-aware default is used.",
    )
    parser.add_argument(
        "--idPersonnel",
        dest="id_personnel",
        type=int,
        default=None,
        help="Optional personnel id to create test RDVs for (default: first doctor found)",
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

    # Allow specifying personnel id via CLI
    doctor, patient = (None, None)
    if args.id_personnel:
        doctor, patient = find_doctor_and_patient_by_id(args.id_personnel)
        if not doctor:
            print(f"ERROR: personnel with id {args.id_personnel} not found")
            raise SystemExit(1)

    if not doctor or not patient:
        # fallback to default discovery
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

    # Generate consecutive appointments
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    slot_count = args.count
    slot_duration = args.duration

    # Dashboard grid shows slots from 08:00 to 18:00.
    # If user provided a start time, use it; otherwise pick a context-aware default.
    if args.start_time:
        try:
            sh, sm = map(int, args.start_time.split(":"))
            base_minutes = sh * 60 + sm
        except Exception:
            base_minutes = max(8 * 60, ((current_minutes - 30) // 30) * 30)
    else:
        base_minutes = max(8 * 60, ((current_minutes - 30) // 30) * 30)

    base_minutes = min(base_minutes, 16 * 60)

    times = []
    for index in range(slot_count):
        start_minutes = base_minutes + (index * slot_duration)
        end_minutes = start_minutes + slot_duration
        times.append((minutes_to_time(start_minutes), minutes_to_time(end_minutes), f"TEST - Consultation {index + 1}"))

    created_ids = []
    for start_time, end_time, motif in times:
        rdv = Rdv(
            idPatient=int(patient["id"]),
            idPersonnel=int(doctor["id"]),
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
    print(f"Doctor ID: {doctor['id']}, Patient ID: {patient['id']}")
    print(f"Date: {test_date.isoformat()}")
    print("\nRDV créés:")
    for index, (start, end, motif) in enumerate(times):
        print(f"  ID {created_ids[index]}: {start} -> {end} ({motif})")

    print("\nPour tester l'urgence patient:")
    print("- ouvre le planning du jour")
    print("- clique un seul RDV test")
    print("- puis clique sur 'Urgence Patient present au cabinet'")
    print("- seul le RDV sélectionné doit être décalé")

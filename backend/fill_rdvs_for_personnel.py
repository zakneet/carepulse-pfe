#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from app import app, db, Planning, Rdv


@dataclass
class Slot:
    date_rdv: date
    start: str
    end: str
    planning_id: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill a doctor's planning with RDVs for every day except Sunday."
    )
    parser.add_argument("--id-personnel", type=int, default=12, help="Personnel ID to fill (default: 12)")
    parser.add_argument(
        "--start-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Start date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to process starting from start-date (default: 7)",
    )
    parser.add_argument(
        "--motif-prefix",
        default="TEST - Remplissage planning",
        help="Prefix used for generated RDV motifs",
    )
    parser.add_argument(
        "--patient-id",
        type=int,
        default=None,
        help="Optional patient ID to reuse for all generated RDVs. If omitted, patients are cycled.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing to the database",
    )
    return parser.parse_args()


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_time(value) -> str:
    if isinstance(value, str):
        if len(value) == 5:
            return f"{value}:00"
        return value
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M:%S")
    raise TypeError(f"Unsupported time value: {value!r}")


def get_patients() -> list[int]:
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(
            """
            SELECT id_patient
            FROM patient
            ORDER BY id_patient ASC
            """
        ).mappings().all()
    return [int(row["id_patient"]) for row in rows]


def get_planning_slots(personnel_id: int, target_date: date) -> list[Slot]:
    plannings = (
        Planning.query.filter_by(idPersonnel=personnel_id, date=target_date)
        .order_by(Planning.heure_debut.asc())
        .all()
    )

    slots: list[Slot] = []
    for planning in plannings:
        start = planning.heure_debut
        end = planning.heure_fin
        step = int(planning.duree_creneau or 30)
        if step <= 0:
            step = 30

        current = datetime.combine(target_date, start)
        limit = datetime.combine(target_date, end)
        while current + timedelta(minutes=step) <= limit:
            slot_start = current.time().strftime("%H:%M:%S")
            slot_end = (current + timedelta(minutes=step)).time().strftime("%H:%M:%S")
            slots.append(Slot(target_date, slot_start, slot_end, planning.idPlanning))
            current += timedelta(minutes=step)

    if slots:
        return slots

    # Fallback used when no explicit planning exists for the day.
    # This keeps the filler usable for personnel accounts that only have RDVs and no saved planning rows.
    default_start = datetime.combine(target_date, datetime.strptime("08:00:00", "%H:%M:%S").time())
    default_end = datetime.combine(target_date, datetime.strptime("18:00:00", "%H:%M:%S").time())
    current = default_start
    while current + timedelta(minutes=30) <= default_end:
        slot_start = current.time().strftime("%H:%M:%S")
        slot_end = (current + timedelta(minutes=30)).time().strftime("%H:%M:%S")
        slots.append(Slot(target_date, slot_start, slot_end, 0))
        current += timedelta(minutes=30)

    return slots


def existing_rdv_pairs(personnel_id: int, target_date: date) -> set[tuple[str, str]]:
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(
            """
            SELECT heureDebut, heureFin
            FROM rdv
            WHERE idPersonnel = %s AND dateRDV = %s
            """,
            (personnel_id, target_date),
        ).mappings().all()

    pairs: set[tuple[str, str]] = set()
    for row in rows:
        pairs.add((format_time(row["heureDebut"]), format_time(row["heureFin"])))
    return pairs


with app.app_context():
    args = parse_args()
    start_date = parse_day(args.start_date)
    end_date = start_date + timedelta(days=max(args.days - 1, 0))
    personnel_id = int(args.id_personnel)

    with db.engine.connect() as conn:
        personnel = conn.exec_driver_sql(
            """
            SELECT id_personnel, nom, prenom, specialite, disponibilite
            FROM personnel_de_sante
            WHERE id_personnel = %s
            LIMIT 1
            """,
            (personnel_id,),
        ).mappings().first()

    if not personnel:
        print(f"ERROR: personnel #{personnel_id} not found")
        raise SystemExit(1)

    patients = [args.patient_id] if args.patient_id else get_patients()
    if not patients:
        print("ERROR: no patient found in database")
        raise SystemExit(1)

    created = 0
    skipped = 0
    patient_index = 0
    created_rows: list[tuple[date, str, str, int]] = []

    for offset in range((end_date - start_date).days + 1):
        target_date = start_date + timedelta(days=offset)
        if target_date.weekday() == 6:
            print(f"Skipping Sunday: {target_date.isoformat()}")
            continue

        slots = get_planning_slots(personnel_id, target_date)
        if not slots:
            print(f"No planning found for {target_date.isoformat()}, skipping")
            continue

        used_pairs = existing_rdv_pairs(personnel_id, target_date)

        for slot in slots:
            pair = (slot.start, slot.end)
            if pair in used_pairs:
                skipped += 1
                continue

            patient_id = patients[patient_index % len(patients)]
            patient_index += 1

            rdv = Rdv(
                idPatient=patient_id,
                idPersonnel=personnel_id,
                dateRDV=slot.date_rdv,
                heureDebut=datetime.strptime(slot.start, "%H:%M:%S").time(),
                heureFin=datetime.strptime(slot.end, "%H:%M:%S").time(),
                motifConsultation=f"{args.motif_prefix} - {slot.date_rdv.isoformat()}",
                statut="consultation",
            )
            db.session.add(rdv)
            created += 1
            created_rows.append((slot.date_rdv, slot.start, slot.end, patient_id))
            used_pairs.add(pair)

    if args.dry_run:
        db.session.rollback()
        print("DRY RUN: no RDV were saved")
    else:
        db.session.commit()

    print("OK: processing complete")
    print(f"Personnel: #{personnel_id} {personnel['prenom']} {personnel['nom']}")
    print(f"Date range: {start_date.isoformat()} -> {end_date.isoformat()}")
    print(f"Created: {created}")
    print(f"Skipped existing overlaps: {skipped}")
    for row in created_rows[:20]:
        print(f"  {row[0].isoformat()} {row[1]}-{row[2]} patient #{row[3]}")
    if len(created_rows) > 20:
        print(f"  ... {len(created_rows) - 20} more")

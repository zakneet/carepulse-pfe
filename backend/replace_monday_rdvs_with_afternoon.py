#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timedelta, time

from app import app, db, Rdv


@dataclass
class ReplacementSlot:
    date_rdv: date
    start: time
    end: time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace Monday RDVs with new afternoon RDVs for a given personnel."
    )
    parser.add_argument("--id-personnel", type=int, default=12, help="Personnel ID to process (default: 12)")
    parser.add_argument(
        "--start-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Start date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to inspect starting from start-date (default: 1)",
    )
    parser.add_argument(
        "--afternoon-start",
        default="13:00",
        help="Afternoon start time in HH:MM format (default: 13:00)",
    )
    parser.add_argument(
        "--afternoon-end",
        default="18:00",
        help="Afternoon end time in HH:MM format (default: 18:00)",
    )
    parser.add_argument(
        "--slot-minutes",
        type=int,
        default=30,
        help="Length of each replacement slot in minutes (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without saving anything",
    )
    return parser.parse_args()


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_clock(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def build_afternoon_slots(target_date: date, start_time: time, end_time: time, slot_minutes: int) -> list[ReplacementSlot]:
    slots: list[ReplacementSlot] = []
    start_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)
    current = start_dt

    while current + timedelta(minutes=slot_minutes) <= end_dt:
        slots.append(
            ReplacementSlot(
                date_rdv=target_date,
                start=current.time(),
                end=(current + timedelta(minutes=slot_minutes)).time(),
            )
        )
        current += timedelta(minutes=slot_minutes)

    return slots


with app.app_context():
    args = parse_args()
    personnel_id = int(args.id_personnel)
    start_date = parse_day(args.start_date)
    end_date = start_date + timedelta(days=max(args.days - 1, 0))
    afternoon_start = parse_clock(args.afternoon_start)
    afternoon_end = parse_clock(args.afternoon_end)
    slot_minutes = int(args.slot_minutes)

    if slot_minutes <= 0:
        print("ERROR: --slot-minutes must be greater than 0")
        raise SystemExit(1)

    with db.engine.connect() as conn:
        personnel = conn.exec_driver_sql(
            """
            SELECT id_personnel, nom, prenom
            FROM personnel_de_sante
            WHERE id_personnel = %s
            LIMIT 1
            """,
            (personnel_id,),
        ).mappings().first()

    if not personnel:
        print(f"ERROR: personnel #{personnel_id} not found")
        raise SystemExit(1)

    monday_dates: list[date] = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 0:
            monday_dates.append(current_date)
        current_date += timedelta(days=1)

    if not monday_dates:
        print("No Monday in the requested range")
        raise SystemExit(0)

    total_deleted = 0
    total_created = 0
    summary: list[str] = []

    for target_date in monday_dates:
        monday_rdvs = (
            Rdv.query.filter_by(idPersonnel=personnel_id, dateRDV=target_date)
            .order_by(Rdv.heureDebut.asc(), Rdv.idRdv.asc())
            .all()
        )

        if not monday_rdvs:
            summary.append(f"{target_date.isoformat()} no RDV found")
            continue

        replacement_slots = build_afternoon_slots(target_date, afternoon_start, afternoon_end, slot_minutes)
        if len(replacement_slots) < len(monday_rdvs):
            print(
                f"ERROR: not enough afternoon slots on {target_date.isoformat()} to replace {len(monday_rdvs)} RDVs "
                f"(available={len(replacement_slots)})"
            )
            raise SystemExit(1)

        planned_pairs = list(zip(monday_rdvs, replacement_slots))

        if args.dry_run:
            summary.append(
                f"{target_date.isoformat()} would delete {len(monday_rdvs)} RDVs and recreate them from {afternoon_start.strftime('%H:%M')}"
            )
            continue

        for rdv in monday_rdvs:
            db.session.delete(rdv)

        for old_rdv, slot in planned_pairs:
            new_rdv = Rdv(
                idPatient=old_rdv.idPatient,
                idPersonnel=old_rdv.idPersonnel,
                dateRDV=slot.date_rdv,
                heureDebut=slot.start,
                heureFin=slot.end,
                motifConsultation=old_rdv.motifConsultation,
                statut=old_rdv.statut,
            )
            db.session.add(new_rdv)

        total_deleted += len(monday_rdvs)
        total_created += len(monday_rdvs)
        summary.append(
            f"{target_date.isoformat()} replaced {len(monday_rdvs)} RDVs with afternoon slots"
        )

    if args.dry_run:
        db.session.rollback()
        print("DRY RUN: no RDV were changed")
    else:
        db.session.commit()

    print("OK: Monday RDV replacement complete")
    print(f"Personnel: #{personnel_id} {personnel['prenom']} {personnel['nom']}")
    print(f"Date range: {start_date.isoformat()} -> {end_date.isoformat()}")
    print(f"Deleted: {total_deleted}")
    print(f"Created: {total_created}")
    for line in summary:
        print(f"  {line}")
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta

from app import app, db, Rdv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete Monday RDVs for a given personnel and date range."
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
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without saving changes",
    )
    return parser.parse_args()


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


with app.app_context():
    args = parse_args()
    personnel_id = int(args.id_personnel)
    start_date = parse_day(args.start_date)
    end_date = start_date + timedelta(days=max(args.days - 1, 0))

    monday_dates: list[date] = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 0:
            monday_dates.append(current_date)
        current_date += timedelta(days=1)

    if not monday_dates:
        print("No Monday in the requested range")
        raise SystemExit(0)

    deleted_ids: list[int] = []
    report: list[str] = []

    for target_date in monday_dates:
        rdvs = (
            Rdv.query.filter_by(idPersonnel=personnel_id, dateRDV=target_date)
            .order_by(Rdv.heureDebut.asc(), Rdv.idRdv.asc())
            .all()
        )

        if not rdvs:
            report.append(f"{target_date.isoformat()} no RDV found")
            continue

        deleted_ids.extend(int(rdv.idRdv) for rdv in rdvs)
        report.append(f"{target_date.isoformat()} delete {len(rdvs)} RDVs")

        if not args.dry_run:
            for rdv in rdvs:
                db.session.delete(rdv)

    if args.dry_run:
        db.session.rollback()
        print("DRY RUN: no RDV were deleted")
    else:
        db.session.commit()

    print("OK: Monday RDV deletion complete")
    print(f"Personnel: #{personnel_id}")
    print(f"Date range: {start_date.isoformat()} -> {end_date.isoformat()}")
    print(f"Deleted: {len(deleted_ids)}")
    if deleted_ids:
        print(f"Deleted IDs: {deleted_ids}")
    for line in report:
        print(f"  {line}")
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date

from app import app, db, Rdv
from sqlalchemy import text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trim RDVs so each day keeps only the first N appointments for a given personnel."
    )
    parser.add_argument("--id-personnel", type=int, default=12, help="Personnel ID to trim (default: 12)")
    parser.add_argument("--keep", type=int, default=5, help="Number of RDVs to keep per day (default: 5)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without saving changes",
    )
    return parser.parse_args()


with app.app_context():
    args = parse_args()
    personnel_id = int(args.id_personnel)
    keep_count = int(args.keep)

    if keep_count <= 0:
        print("ERROR: --keep must be greater than 0")
        raise SystemExit(1)

    rows = db.session.execute(
        text(
            """
            SELECT idRDV, dateRDV, heureDebut, heureFin, motifConsultation
            FROM rdv
            WHERE idPersonnel = :id_personnel
            ORDER BY dateRDV ASC, heureDebut ASC, idRDV ASC
            """
        ),
        {"id_personnel": personnel_id},
    ).mappings().all()

    if not rows:
        print(f"No RDVs found for personnel #{personnel_id}")
        raise SystemExit(0)

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["dateRDV"]].append(row)

    to_delete_ids = []
    report = []
    for day, day_rows in grouped.items():
        if len(day_rows) > keep_count:
            extras = day_rows[keep_count:]
            to_delete_ids.extend(int(item["idRDV"]) for item in extras)
            report.append((day, len(day_rows), keep_count, [int(item["idRDV"]) for item in extras]))
        else:
            report.append((day, len(day_rows), len(day_rows), []))

    if args.dry_run:
        print("DRY RUN: no RDV were deleted")
    else:
        for rdv_id in to_delete_ids:
            rdv = Rdv.query.get(rdv_id)
            if rdv:
                db.session.delete(rdv)
        db.session.commit()

    print(f"Personnel: #{personnel_id}")
    print(f"Keep per day: {keep_count}")
    print(f"Days processed: {len(grouped)}")
    print(f"RDVs deleted: {len(to_delete_ids)}")
    for day, before, after, deleted_ids in report:
        suffix = f" deleted={deleted_ids}" if deleted_ids else ""
        print(f"  {day.isoformat()} before={before} after={after}{suffix}")

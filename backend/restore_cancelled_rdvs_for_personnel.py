#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict

from app import app, db, Rdv
from sqlalchemy import text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore cancelled RDVs for a given personnel by removing the cancellation prefix."
    )
    parser.add_argument("--id-personnel", type=int, default=12, help="Personnel ID to restore (default: 12)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be restored without saving changes",
    )
    return parser.parse_args()


def strip_cancel_prefix(motif: str | None) -> str:
    value = (motif or "").strip()
    if value.lower().startswith("annule - "):
        return value[9:].strip() or "consultation"
    if value.lower().startswith("annule"):
        return value.split("-", 1)[-1].strip() if "-" in value else "consultation"
    return value or "consultation"


with app.app_context():
    args = parse_args()
    personnel_id = int(args.id_personnel)

    rows = db.session.execute(
        text(
            """
            SELECT idRDV, dateRDV, heureDebut, heureFin, motifConsultation, statut
            FROM rdv
            WHERE idPersonnel = :id_personnel
              AND (statut LIKE 'annule%' OR motifConsultation LIKE 'Annule - %' OR motifConsultation LIKE 'annule - %')
            ORDER BY dateRDV ASC, heureDebut ASC, idRDV ASC
            """
        ),
        {"id_personnel": personnel_id},
    ).mappings().all()

    if not rows:
        print(f"No cancelled RDVs found for personnel #{personnel_id}")
        raise SystemExit(0)

    grouped = defaultdict(int)
    restored_ids: list[int] = []

    for row in rows:
        rdv = db.session.get(Rdv, int(row["idRDV"]))
        if not rdv:
            continue

        rdv.motifConsultation = strip_cancel_prefix(rdv.motifConsultation)
        rdv.statut = "consultation"
        restored_ids.append(int(rdv.idRdv))
        grouped[row["dateRDV"]] += 1

    if args.dry_run:
        db.session.rollback()
        print("DRY RUN: no RDV were restored")
    else:
        db.session.commit()

    print(f"Personnel: #{personnel_id}")
    print(f"Restored RDVs: {len(restored_ids)}")
    for day, count in sorted(grouped.items()):
        print(f"  {day.isoformat()} restored={count}")
    if restored_ids:
        preview = ", ".join(str(x) for x in restored_ids[:20])
        print(f"RDV IDs: {preview}{' ...' if len(restored_ids) > 20 else ''}")

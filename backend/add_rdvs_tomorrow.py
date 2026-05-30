#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse

from app import app, db, Rdv


def parse_args():
    parser = argparse.ArgumentParser(description="Add RDVs for tomorrow (simple helper)")
    parser.add_argument("--date", dest="date_value", default=None, help="Target date YYYY-MM-DD (defaults to tomorrow)")
    parser.add_argument("--count", dest="count", type=int, default=6, help="Number of RDVs to create")
    parser.add_argument("--duration", dest="duration", type=int, default=30, help="Duration in minutes (default 30)")
    parser.add_argument("--start", dest="start_time", default="09:00", help="Start time for first slot (HH:MM) default 09:00")
    parser.add_argument("--idPersonnel", dest="id_personnel", type=int, default=1, help="Personnel id to assign the RDVs")
    parser.add_argument("--idPatient", dest="id_patient", type=int, default=1, help="Patient id to assign the RDVs")
    return parser.parse_args()


def minutes_to_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}:00"


with app.app_context():
    args = parse_args()
    if args.date_value:
        target_date = datetime.strptime(args.date_value, "%Y-%m-%d").date()
    else:
        target_date = (datetime.now() + timedelta(days=1)).date()

    # parse start_time
    try:
        sh, sm = map(int, args.start_time.split(":"))
        base_minutes = sh * 60 + sm
    except Exception:
        base_minutes = 9 * 60

    times = []
    for i in range(args.count):
        start = base_minutes + i * args.duration
        end = start + args.duration
        times.append((minutes_to_time(start), minutes_to_time(end)))

    created = []
    for start_time, end_time in times:
        rdv = Rdv(
            idPatient=int(args.id_patient),
            idPersonnel=int(args.id_personnel),
            dateRDV=target_date,
            heureDebut=start_time,
            heureFin=end_time,
            motifConsultation=f"AUTO - Rendez-vous {start_time}",
        )
        db.session.add(rdv)
        db.session.flush()
        created.append(getattr(rdv, 'idRdv', getattr(rdv, 'idRDV', None)))

    db.session.commit()

    print(f"OK: Created {len(created)} RDVs for {target_date.isoformat()} for personnel {args.id_personnel}")
    for idx, (start_time, end_time) in enumerate(times):
        print(f"  ID {created[idx]}: {start_time} -> {end_time}")

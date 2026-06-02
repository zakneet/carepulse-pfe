"""
Seed Dr Meher Labidi (id_personnel=1) with:
- access code 5AZUY6
- planning windows 08:00-17:30 for weekdays, today + 60 days
- simulated Tunisian patients
- appointments (~40% slot occupancy on weekdays)

Run: python backend/seed_meher_planning.py
"""
import random
from datetime import date, datetime, timedelta, time

import pymysql

DOCTOR_ID = 1
ACCESS_CODE = "5AZUY6"
DB = dict(host="localhost", user="root", password="", database="gestion_des-rendez-vous5", charset="utf8mb4")
SLOT_START = time(8, 0)
SLOT_END = time(17, 30)
SLOT_MINUTES = 30
DAYS_AHEAD = 60

PATIENTS = [
    ("Ben Salah", "Amira"), ("Trabelsi", "Karim"), ("Mansour", "Leila"), ("Haddad", "Youssef"),
    ("Gharbi", "Sami"), ("Cherif", "Nadia"), ("Bouazizi", "Rim"), ("Jaziri", "Walid"),
    ("Mabrouk", "Safa"), ("Ayari", "Mehdi"), ("Riahi", "Imen"), ("Khlifi", "Anis"),
    ("Zitouni", "Salma"), ("Amri", "Hichem"), ("Baccouche", "Mouna"), ("Miled", "Kamel"),
    ("Sassi", "Fatma"), ("Touati", "Ali"), ("Zouari", "Asma"), ("Jemai", "Nizar"),
    ("Oueslati", "Sarra"), ("Tlili", "Amine"), ("Ghannouchi", "Yasmine"), ("Khemiri", "Omar"),
    ("Bouhlel", "Ines"), ("Ferchichi", "Tarek"), ("Hamdi", "Lina"), ("Nasri", "Fares"),
    ("Slimani", "Hela"), ("Dridi", "Bilel"),
]

MOTIFS = [
    "Consultation generale", "Suivi pediatrique", "Bilan annuel", "Controle croissance",
    "Vaccination", "Suivi asthme", "Douleur abdominale", "Fievre persistante",
    "Consultation ORL", "Suivi allergie", "Certificat medical", "Premiere consultation",
]


def slot_times():
    start_min = SLOT_START.hour * 60 + SLOT_START.minute
    end_min = SLOT_END.hour * 60 + SLOT_END.minute
    cursor = start_min
    while cursor + SLOT_MINUTES <= end_min:
        h, m = divmod(cursor, 60)
        yield time(h, m)
        cursor += SLOT_MINUTES


def main():
    random.seed(2026)
    today = date.today()
    end_date = today + timedelta(days=DAYS_AHEAD)

    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO personnel_de_sante (id_personnel, nom, prenom, specialite, disponibilite, region, access_code)
                VALUES (%s, 'Labidi', 'Meher', 'Pediatre', 1, 'Ariana Ville', %s)
                ON DUPLICATE KEY UPDATE
                    nom='Labidi', prenom='Meher', specialite='Pediatre',
                    disponibilite=1, region='Ariana Ville', access_code=%s
                """,
                (DOCTOR_ID, ACCESS_CODE, ACCESS_CODE),
            )

            cur.execute("DELETE FROM rdv WHERE idPersonnel = %s AND dateRDV >= %s", (DOCTOR_ID, today))
            cur.execute("DELETE FROM planning WHERE idPersonnel = %s AND date >= %s", (DOCTOR_ID, today))

            patient_ids = []
            for nom, prenom in PATIENTS:
                cur.execute(
                    "SELECT id_patient FROM patient WHERE nom=%s AND prenom=%s LIMIT 1",
                    (nom, prenom),
                )
                row = cur.fetchone()
                if row:
                    patient_ids.append(row["id_patient"])
                else:
                    cur.execute(
                        "INSERT INTO patient (nom, prenom, telephone) VALUES (%s, %s, %s)",
                        (nom, prenom, f"+216{random.randint(20000000, 99999999)}"),
                    )
                    patient_ids.append(cur.lastrowid)

            appt_count = 0
            day = today
            while day <= end_date:
                if day.weekday() < 5:
                    cur.execute(
                        """
                        INSERT INTO planning (date, heureDebut, heureFin, duree_creneau, idPersonnel)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (day, SLOT_START, SLOT_END, SLOT_MINUTES, DOCTOR_ID),
                    )

                    slots = list(slot_times())
                    random.shuffle(slots)
                    booked = slots[: max(3, int(len(slots) * random.uniform(0.35, 0.55)))]

                    for slot_start in sorted(booked):
                        end_h, end_m = divmod(slot_start.hour * 60 + slot_start.minute + SLOT_MINUTES, 60)
                        slot_end = time(end_h, end_m)
                        pid = random.choice(patient_ids)
                        motif = random.choice(MOTIFS)
                        if random.random() < 0.04:
                            motif = f"Urgence - {motif}"
                        cur.execute(
                            """
                            INSERT INTO rdv (idPatient, idPersonnel, dateRDV, heureDebut, heureFin, motifConsultation)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (pid, DOCTOR_ID, day, slot_start, slot_end, motif),
                        )
                        appt_count += 1
                day += timedelta(days=1)

        conn.commit()
        print(f"Seeded Dr Meher Labidi: {len(patient_ids)} patients, {appt_count} appointments, planning until {end_date}.")
        print(f"Access code: {ACCESS_CODE}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

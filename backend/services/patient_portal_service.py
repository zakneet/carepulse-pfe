"""OptiClinic — secure patient portal tokens, documents, portal payload."""
import secrets
from datetime import datetime, timedelta

PENDING_PREFIX = "En attente - "
CONFIRMED_PREFIX = "Consultation confirmée - "
TOKEN_EXPIRY_DAYS = 90


def ensure_portal_tables(conn):
    conn.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS patient_portal_token (
            id INT NOT NULL AUTO_INCREMENT,
            token VARCHAR(128) NOT NULL,
            id_patient INT NOT NULL,
            id_rdv INT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            PRIMARY KEY (id),
            UNIQUE KEY uq_portal_token (token),
            KEY idx_portal_patient (id_patient)
        ) ENGINE=InnoDB
        """
    )
    conn.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS patient_document (
            id INT NOT NULL AUTO_INCREMENT,
            id_patient INT NOT NULL,
            id_rdv INT NULL,
            doc_type VARCHAR(64) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content MEDIUMTEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_doc_patient (id_patient)
        ) ENGINE=InnoDB
        """
    )


def generate_secure_token() -> str:
    return secrets.token_urlsafe(48)


def is_pending_motif(motif: str | None) -> bool:
    lowered = (motif or "").lower()
    return lowered.startswith("en attente") or "[pending]" in lowered


def derive_rdv_statut(motif: str | None) -> str:
    lowered = (motif or "").lower()
    if is_pending_motif(motif):
        return "En attente"
    if "urgence" in lowered or "urgent" in lowered:
        return "Urgence"
    if any(t in lowered for t in ("replac", "replanif", "deplace", "optimis")):
        return "Optimise"
    if "confirm" in lowered or lowered.startswith("consultation"):
        return "Confirme"
    return "Confirme"


def confirm_motif(motif: str | None) -> str:
    raw = (motif or "consultation").strip()
    if raw.lower().startswith("en attente - "):
        raw = raw[len("En attente - ") :].strip()
    elif raw.lower().startswith("en attente"):
        raw = raw.replace("En attente", "", 1).strip(" -")
    if not raw or raw.lower() == "consultation":
        return "Consultation confirmée"
    if not raw.lower().startswith("consultation confirm"):
        return f"{CONFIRMED_PREFIX}{raw}"
    return raw


def create_portal_token(conn, id_patient: int, id_rdv: int | None = None) -> str:
    ensure_portal_tables(conn)
    token = generate_secure_token()
    expires = datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    conn.exec_driver_sql(
        """
        UPDATE patient_portal_token SET is_active = 0
        WHERE id_patient = %s AND is_active = 1
        """,
        (int(id_patient),),
    )
    conn.exec_driver_sql(
        """
        INSERT INTO patient_portal_token (token, id_patient, id_rdv, expires_at, is_active)
        VALUES (%s, %s, %s, %s, 1)
        """,
        (token, int(id_patient), id_rdv, expires),
    )
    return token


def resolve_token(conn, token: str):
    ensure_portal_tables(conn)
    row = conn.exec_driver_sql(
        """
        SELECT id, token, id_patient, id_rdv, expires_at, is_active
        FROM patient_portal_token
        WHERE token = %s AND is_active = 1
        LIMIT 1
        """,
        (token.strip(),),
    ).mappings().first()
    if not row:
        return None
    expires = row["expires_at"]
    if expires and expires < datetime.utcnow():
        return None
    return row


def generate_patient_documents(conn, id_patient: int, id_rdv: int, patient_name: str, doctor_name: str, date_label: str):
    ensure_portal_tables(conn)
    docs = [
        (
            "prescription",
            "Ordonnance médicale",
            f"""ORDONNANCE MÉDICALE — OptiClinic
Patient: {patient_name}
Médecin: Dr. {doctor_name}
Date: {date_label}

1. Paracétamol 500 mg — 1 comprimé toutes les 6 heures si douleur
2. Repos et hydratation abondante
3. Contrôle dans 7 jours si persistance des symptômes

Dr. {doctor_name}
Cabinet OptiClinic""",
        ),
        (
            "consultation_report",
            "Compte-rendu de consultation",
            f"""COMPTE-RENDU DE CONSULTATION — OptiClinic
Patient: {patient_name}
Médecin: Dr. {doctor_name}
Date: {date_label}

Motif: Consultation de suivi
Examen: Paramètres vitaux stables
Conclusion: Évolution favorable
Recommandations: Poursuite du traitement prescrit

Dr. {doctor_name}""",
        ),
        (
            "blood_test",
            "Résultat analyse de sang",
            f"""RÉSULTAT ANALYSE SANG — OptiClinic
Patient: {patient_name}
Date: {date_label}

Hémoglobine: 13.8 g/dL (N)
Leucocytes: 6.2 10³/µL (N)
Plaquettes: 245 10³/µL (N)
Glycémie: 0.92 g/L (N)

Interprétation: Bilan biologique dans les normes.
Dr. {doctor_name}""",
        ),
        (
            "medical_certificate",
            "Certificat médical",
            f"""CERTIFICAT MÉDICAL — OptiClinic
Je soussigné(e) Dr. {doctor_name}, certifie avoir examiné ce jour
{patient_name}.

État de santé compatible avec une reprise d'activité normale.

Fait à Tunis, le {date_label}.
Dr. {doctor_name}""",
        ),
    ]

    created = []
    for doc_type, title, content in docs:
        existing = conn.exec_driver_sql(
            """
            SELECT id FROM patient_document
            WHERE id_patient = %s AND id_rdv = %s AND doc_type = %s
            LIMIT 1
            """,
            (int(id_patient), int(id_rdv), doc_type),
        ).mappings().first()
        if existing:
            continue
        conn.exec_driver_sql(
            """
            INSERT INTO patient_document (id_patient, id_rdv, doc_type, title, content)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (int(id_patient), int(id_rdv), doc_type, title, content),
        )
        created.append({"type": doc_type, "title": title})
    return created

from datetime import datetime, timedelta
import functools
import os
import threading

from flask import Flask, jsonify, request, render_template, session, abort, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import jwt
from ortools.sat.python import cp_model
from sqlalchemy import text
import smtplib
from email.message import EmailMessage
import json
try:
    from pywebpush import webpush, WebPushException
    _HAS_PYWEBPUSH = True
except Exception:
    _HAS_PYWEBPUSH = False
app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

# Enable CORS for Angular frontend.
CORS(app, resources={r"/*": {"origins": "*"}})

# Enable Socket.IO with CORS for Angular frontend.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# MySQL configuration.
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "gestion_des_rendez-vous")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
DB_READY = False

# Make project root importable so we can reuse services.weather_service
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from services.weather_service import get_weather, get_current_weather
except Exception:
    # Fallback: define a minimal get_weather that returns unavailable
    def get_weather(city: str):
        return {"status": "error", "message": "weather unavailable", "status_code": 502, "weather_recommendation": "Météo indisponible", "current_weather": {}}

    def get_current_weather(lat: float, lon: float):
        return {"status": "error", "message": "weather unavailable", "status_code": 502, "weather_recommendation": "Météo indisponible", "current_weather": {}}

try:
    from services.traffic_service import get_default_start_coords, get_traffic_notice, get_travel_notice
except Exception:
    def get_default_start_coords():
        return (10.10, 36.80)

    def get_traffic_notice(start_coords, end_coords):
        return {"status": "error", "recommendation": "Information trafic indisponible", "duration_normal": None, "duration_current": None, "traffic_delay_percent": None}

    def get_travel_notice(patient_address, clinic_address, appointment_time):
        return {"status": "error", "recommendation": "Information trafic indisponible", "duration_normal": None, "duration_current": None, "traffic_delay_percent": None}

DEFAULT_CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "Clinique OptiClinic, Tunis, Tunisie")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:4200")
# SMTP notification configuration (optional). If not set, emails will be skipped and logged.
NOTIF_SMTP_HOST = os.getenv("NOTIF_SMTP_HOST")
NOTIF_SMTP_PORT = int(os.getenv("NOTIF_SMTP_PORT", "0")) if os.getenv("NOTIF_SMTP_PORT") else None
NOTIF_SMTP_USER = os.getenv("NOTIF_SMTP_USER")
NOTIF_SMTP_PASS = os.getenv("NOTIF_SMTP_PASS")
NOTIF_FROM_EMAIL = os.getenv("NOTIF_FROM_EMAIL", "no-reply@gestion-rdv.local")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", f"mailto:{NOTIF_FROM_EMAIL}")

def _send_email(to_email: str, subject: str, body: str) -> bool:
    """Send a plain-text email using configured SMTP server. Returns True on success."""
    if not NOTIF_SMTP_HOST or not NOTIF_SMTP_PORT:
        print("[notify] SMTP not configured, skipping email send", flush=True)
        return False
    try:
        msg = EmailMessage()
        msg["From"] = NOTIF_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(NOTIF_SMTP_HOST, NOTIF_SMTP_PORT, timeout=10) as s:
            s.ehlo()
            if NOTIF_SMTP_USER and NOTIF_SMTP_PASS:
                try:
                    s.starttls()
                except Exception:
                    pass
                s.login(NOTIF_SMTP_USER, NOTIF_SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception as exc:
        print(f"[notify] Failed to send email to {to_email}: {exc}", flush=True)
        return False


def _notify_patients_of_reschedule(updated_rows: list, date_rdv):
    """Notify patients by email (if available) about their new slot after reschedule."""
    if not updated_rows:
        return
    for r in updated_rows:
        try:
            patient_id = int(r.get("idPatient") or 0)
        except Exception:
            continue
        if not patient_id:
            continue
        with db.engine.connect() as conn:
            patient = conn.exec_driver_sql(
                "SELECT prenom, nom, email, telephone FROM patient WHERE id_patient = %s LIMIT 1",
                (patient_id,),
            ).mappings().first()

        if not patient:
            continue

        new_time = f"{r.get('heureDebut')} - {r.get('heureFin')}"
        previous = r.get("previousHeureDebut") or r.get("previousStart")
        subject = "Changement de votre rendez-vous"
        body = (
            f"Bonjour {patient.get('prenom') or ''},\n\n"
            f"Votre rendez-vous prévu le {date_rdv.isoformat()} a été déplacé à {new_time} en raison d'une urgence médicale.\n\n"
            "Souhaitez-vous modifier ce créneau ? Répondez à cet e-mail ou contactez la clinique. "
            f"Vous pouvez aussi gérer vos rendez-vous ici: {FRONTEND_URL}/patient/appointments\n\n"
            "Cordialement,\nClinique"
        )

        if patient.get("email"):
            sent = _send_email(patient.get("email"), subject, body)
            print(f"[notify] email sent={sent} to {patient.get('email')}", flush=True)
        else:
            print(f"[notify] no email for patient {patient_id}, telephone={patient.get('telephone')}", flush=True)

        # Send Web Push if subscription exists for this patient
        payload = {
            "title": "Changement de rendez-vous",
            "body": f"Votre rendez-vous du {date_rdv.isoformat()} a été déplacé à {new_time}",
            "url": f"{FRONTEND_URL}/patient/appointments",
            "rdvId": r.get("id"),
        }
        try:
            for sub in list(PUSH_SUBSCRIPTIONS):
                try:
                    if not isinstance(sub, dict):
                        continue
                    # Expect frontend to include 'patientId' in subscription record
                    if int(sub.get("patientId") or 0) != int(patient_id):
                        continue
                    _send_webpush(sub.get("subscription") or sub, payload)
                except Exception:
                    continue
        except Exception:
            pass


def _notify_patients_of_cancellation(rdv_ids: list, target_date):
    if not rdv_ids:
        return
    for rdv_id in rdv_ids:
        try:
            with db.engine.connect() as conn:
                row = conn.exec_driver_sql(
                    "SELECT p.prenom, p.nom, p.email, p.telephone, r.heureDebut, r.heureFin, r.idPatient "
                    "FROM rdv r JOIN patient p ON p.id_patient = r.idPatient WHERE r.idRDV = %s LIMIT 1",
                    (rdv_id,),
                ).mappings().first()

            if not row:
                continue

            time_text = f"{_format_time_for_client(row.get('heureDebut'))} - {_format_time_for_client(row.get('heureFin'))}"
            subject = "Annulation de votre rendez-vous"
            body = (
                f"Bonjour {row.get('prenom') or ''},\n\n"
                f"Votre rendez-vous prévu le {target_date.isoformat()} à {time_text} a été annulé en raison d'une urgence médicale.\n\n"
                f"Cordialement,\n"
                f"L'équipe médicale"
            )

            if row.get('email'):
                sent = _send_email(row.get('email'), subject, body)
                print(f"[notify] cancellation email sent={sent} to {row.get('email')}", flush=True)
            else:
                print(f"[notify] no email for patient of rdv {rdv_id}, tel={row.get('telephone')}", flush=True)

            payload = {
                "title": "Rendez-vous annulé",
                "body": f"Votre rendez-vous du {target_date.isoformat()} a été annulé.",
                "url": f"{FRONTEND_URL}/patient/appointments",
                "rdvId": rdv_id,
            }
            try:
                for sub in list(PUSH_SUBSCRIPTIONS):
                    try:
                        if not isinstance(sub, dict):
                            continue
                        if int(sub.get("patientId") or 0) != int(row.get("idPatient") or 0):
                            continue
                        _send_webpush(sub.get("subscription") or sub, payload)
                    except Exception:
                        continue
            except Exception:
                pass
        except Exception:
            pass
def _send_webpush(subscription_info, payload: dict) -> bool:
    """Send a Web Push notification using pywebpush. subscription_info should
    be the object returned by `pushManager.subscribe()` on the client.
    Returns True on success.
    """
    if not _HAS_PYWEBPUSH or not VAPID_PRIVATE_KEY:
        print("[notify] WebPush not available or VAPID key missing, skipping", flush=True)
        return False
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return True
    except WebPushException as ex:
        print(f"[notify] WebPushException: {ex}", flush=True)
        return False
    except Exception as exc:
        print(f"[notify] WebPush send failed: {exc}", flush=True)
        return False


try:
    from services.optimal_departure_service import get_optimal_departure, resolve_city_coordinates
except Exception:
    def resolve_city_coordinates(city):
        return (10.10, 36.80)

    def get_optimal_departure(start_coords, end_coords, city):
        return {"status": "error", "recommendation": "Information de départ indisponible", "base_duration": None, "traffic_duration": None, "weather_penalty": None, "traffic_penalty": None, "final_duration": None, "tone": "normal"}

USER_STATUS = {1: "patient", 2: "personnel medical"}
RDV_STATUTS = {"urgence", "consultation", "controle", "confirme", "decale (urgence patient)", "annule (urgence medecin)"}
RDV_CREATION_STATUTS = {"consultation", "controle"}
RDV_URGENT_STATUT = "urgence"
TRAVEL_NOTICE_CACHE: dict[tuple[int, int], dict] = {}
TRAVEL_NOTICE_REFRESH_SECONDS = int(os.getenv("TRAVEL_NOTICE_REFRESH_SECONDS", "900"))
TRAVEL_NOTICE_WINDOW_MINUTES = int(os.getenv("TRAVEL_NOTICE_WINDOW_MINUTES", "120"))
TRAVEL_NOTICE_CACHE_TTL_SECONDS = int(os.getenv("TRAVEL_NOTICE_CACHE_TTL_SECONDS", "1800"))
TRAVEL_NOTICE_WORKER_STARTED = False


def _normalize_status(value):
    if value is None:
        return ""

    normalized = str(value).strip().lower()
    return (
        normalized
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ç", "c")
    )


def debug_route(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            print(f"\n>>> DEBUG ROUTE {func.__name__} called: path={request.path} args={dict(request.args)}", flush=True)
            if request.is_json:
                print(f"    JSON body: {request.get_json(silent=True)}", flush=True)
            else:
                raw = request.get_data(as_text=True)
                if raw:
                    print(f"    Raw body: {raw}", flush=True)
        except Exception as e:
            print(f">>> DEBUG ROUTE logging failed: {str(e)}", flush=True)
        return func(*args, **kwargs)
    return wrapper


@app.route("/weather", methods=["GET"])
def weather_api():
    """Return current weather by coordinates or by city name."""
    try:
        latitude = request.args.get("latitude", type=float)
        longitude = request.args.get("longitude", type=float)
        city = (request.args.get("city") or request.args.get("ville") or "").strip()

        if latitude is not None and longitude is not None:
            return jsonify(get_current_weather(latitude, longitude)), 200

        if city:
            return jsonify(get_weather(city)), 200

        return jsonify({
            "status": "error",
            "message": "latitude/longitude ou city sont obligatoires",
            "status_code": 400,
            "weather_recommendation": "Météo indisponible",
            "current_weather": {},
        }), 400
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": f"erreur serveur: {str(exc)}",
            "status_code": 500,
            "weather_recommendation": "Météo indisponible",
            "current_weather": {},
        }), 500


@app.route('/manifest.json')
def manifest_route():
    """Serve manifest.json from the static folder so browsers can fetch /manifest.json."""
    return send_from_directory('static', 'manifest.json')


@app.route('/offline')
def offline_page():
    """Render a friendly offline page used by the service worker as fallback."""
    return render_template('offline.html')


@app.route('/sw.js')
@app.route('/service-worker.js')
def service_worker():
    """Expose the service worker at the site root so it can control the whole origin scope."""
    return send_from_directory(os.path.join('static', 'js'), 'sw.js')


# --- PUSH subscription placeholders ---------------------------------
# The following endpoints provide a minimal, safe storage for push subscriptions.
# They are intentionally simple: a production-ready implementation should store
# subscriptions in a persistent database and use WebPush (pywebpush) with VAPID keys
# to send notifications to clients. This placeholder keeps routes available
# and documents where to implement VAPID authentication later.

PUSH_SUBSCRIPTIONS = []


@app.route('/push/subscribe', methods=['POST'])
def push_subscribe():
    """Store a push subscription (JSON) sent from the client.

    Production: validate the payload, persist the subscription, and return
    a resource ID. For now we accept and keep it in memory to ease local testing.
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'status': 'error', 'message': 'payload missing'}), 400
        PUSH_SUBSCRIPTIONS.append(data)
        return jsonify({'status': 'success', 'stored': True}), 201
    except Exception:
        return jsonify({'status': 'error', 'message': 'invalid payload'}), 400


@app.route('/push/subscriptions', methods=['GET'])
def push_list():
    """Return current in-memory push subscriptions (debug only)."""
    return jsonify({'count': len(PUSH_SUBSCRIPTIONS), 'subscriptions': PUSH_SUBSCRIPTIONS})



class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(30), nullable=True)
    cin = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    specialite = db.Column(db.String(120), nullable=True)
    disponibilite = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False, default="")
    access_code = db.Column(db.String(120), nullable=True, unique=True)
    statut = db.Column("role", db.Integer, nullable=False)
    
   

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "telephone": self.telephone,
            "cin": self.cin,
            "email": self.email,
            "specialite": self.specialite,
            "disponibilite": self.disponibilite,
            "statut": self.statut,
            "statut_label": USER_STATUS.get(self.statut, "inconnu"),
        }


class Patient(db.Model):
    __tablename__ = 'patient'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id_patient = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(30), nullable=True)


class PersonnelDeSante(db.Model):
    __tablename__ = 'personnel_de_sante'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id_personnel = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(120), nullable=True)
    disponibilite = db.Column(db.Boolean, nullable=False, default=True)


def _ensure_personnel_table_columns():
    with db.engine.begin() as conn:
        existing_columns = {
            row[0]
            for row in conn.exec_driver_sql(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'personnel_de_sante'
                """
            ).fetchall()
        }

        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS personnel_de_sante (
                id_personnel INT NOT NULL AUTO_INCREMENT,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                specialite VARCHAR(120) NULL,
                    region VARCHAR(120) NULL,
                disponibilite TINYINT(1) NOT NULL DEFAULT 1,
                PRIMARY KEY (id_personnel)
            ) ENGINE=InnoDB
            """
        )
        
        if "specialite" not in existing_columns:
            try:
                conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `specialite` VARCHAR(120) NULL")
            except Exception:
                pass
                
        if "region" not in existing_columns:
            try:
                conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `region` VARCHAR(120) NULL")
            except Exception:
                pass
        if "disponibilite" not in existing_columns:
            try:
                conn.exec_driver_sql("ALTER TABLE personnel_de_sante ADD COLUMN `disponibilite` TINYINT(1) NOT NULL DEFAULT 1")
            except Exception:
                pass

        for legacy_column in ("telephone", "email", "ville", "type_personnel", "password", "access_code"):
            if legacy_column in existing_columns:
                try:
                    conn.exec_driver_sql(f"ALTER TABLE personnel_de_sante DROP COLUMN `{legacy_column}`")
                except Exception:
                    pass



class Planning(db.Model):
    __tablename__ = 'planning'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    
    idPlanning = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    heure_debut = db.Column("heureDebut", db.Time, nullable=False)
    heure_fin = db.Column("heureFin", db.Time, nullable=False)
    duree_creneau = db.Column(db.Integer, nullable=False, default=30)
    idPersonnel = db.Column(db.Integer, nullable=False, index=True)

    def to_dict(self):
        return {
            "idPlanning": self.idPlanning,
            "date": self.date.isoformat(),
            "heure_debut": _format_sql_time(self.heure_debut),
            "heure_fin": _format_sql_time(self.heure_fin),
            "duree_creneau": self.duree_creneau,
            "idPersonnel": self.idPersonnel,
        }


class Rdv(db.Model):
    __tablename__ = 'rdv'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    
    idRdv = db.Column("idRDV", db.Integer, primary_key=True, autoincrement=True)
    idPatient = db.Column(db.Integer, nullable=False, index=True)
    idPersonnel = db.Column(db.Integer, nullable=False, index=True)
    dateRDV = db.Column(db.Date, nullable=False)
    heureDebut = db.Column(db.Time, nullable=False)
    heureFin = db.Column(db.Time, nullable=False)
    motifConsultation = db.Column(db.Text, nullable=False, default="")
    statut = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.idRdv,
            "idRdv": self.idRdv,
            "idRDV": self.idRdv,
            "idPatient": self.idPatient,
            "idPersonnel": self.idPersonnel,
            "dateRDV": self.dateRDV.isoformat(),
            "heureDebut": _format_sql_time(self.heureDebut),
            "heureFin": _format_sql_time(self.heureFin),
            "motifConsultation": self.motifConsultation,
            "statut": self.statut,
        }


# Compatibility alias for legacy scripts that import RDV instead of Rdv.
RDV = Rdv


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def parse_time(value):
    if value is None:
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except (TypeError, ValueError):
            continue

    return None


def _generate_unique_patient_email(prefix="patient"):
    import time

    base_suffix = int(time.time() * 1000) % 1000000
    for attempt in range(20):
        suffix = f"{base_suffix + attempt:06d}"
        email = f"{prefix}_{suffix}@gestion-rdv.local"
        with db.engine.connect() as conn:
            existing = conn.exec_driver_sql(
                """
                SELECT id_patient FROM patient
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (email,),
            ).mappings().first()
        if not existing:
            return email

    return f"{prefix}_{int(time.time() * 1000)}@gestion-rdv.local"


def _split_health_values(value):
    if value is None:
        return []

    cleaned = str(value).replace("\n", ",").replace(";", ",")
    return [part.strip() for part in cleaned.split(",") if part.strip()]


def _compute_age(date_value):
    if not date_value:
        return None

    if isinstance(date_value, datetime):
        birth_date = date_value.date()
    elif hasattr(date_value, "year") and hasattr(date_value, "month") and hasattr(date_value, "day"):
        birth_date = date_value
    else:
        try:
            birth_date = datetime.strptime(str(date_value), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    today = datetime.utcnow().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age if age >= 0 else None


def _ensure_optional_user_columns():
    optional_columns = {
        "cin": "VARCHAR(50) NULL",
        "sexe": "VARCHAR(20) NULL",
        "date_naissance": "DATE NULL",
        "allergies": "TEXT NULL",
        "maladies": "TEXT NULL",
    }

    with db.engine.begin() as conn:
        existing_columns = {
            row[0]
            for row in conn.exec_driver_sql(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'user'
                """
            ).fetchall()
        }

        for column_name, ddl in optional_columns.items():
            if column_name in existing_columns:
                continue
            try:
                conn.exec_driver_sql(f"ALTER TABLE user ADD COLUMN `{column_name}` {ddl}")
            except Exception:
                # Keep API available even if schema migration rights are restricted.
                pass


def _ensure_patient_table_columns():
    with db.engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS patient (
                id_patient INT NOT NULL AUTO_INCREMENT,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                telephone VARCHAR(30) NULL,
                PRIMARY KEY (id_patient)
            ) ENGINE=InnoDB
            """
        )
        for column_name in ("email", "adresse", "cin", "password"):
            try:
                conn.exec_driver_sql(f"ALTER TABLE patient DROP COLUMN IF EXISTS `{column_name}`")
            except Exception:
                pass
    _ensure_rdv_table_columns()
    _ensure_personnel_table_columns()


def _ensure_rdv_table_columns():
    with db.engine.begin() as conn:
        existing_columns = {
            row[0]
            for row in conn.exec_driver_sql(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'rdv'
                """
            ).fetchall()
        }

        if "statut" in existing_columns:
            try:
                conn.exec_driver_sql("ALTER TABLE rdv DROP COLUMN `statut`")
            except Exception:
                # Keep API available even if schema migration rights are restricted.
                pass


def _get_personnel_row(id_personnel):
    with db.engine.connect() as conn:
        return conn.exec_driver_sql(
            """
            SELECT id_personnel, nom, prenom, specialite, region, disponibilite
            FROM personnel_de_sante
            WHERE id_personnel = %s
            LIMIT 1
            """,
            (int(id_personnel),),
        ).mappings().first()


@app.route('/appointments')
def appointments_page():
    # Secure: require logged in user via session
    user_id = session.get('user_id')
    if not user_id:
        return abort(403)

    # Query RDVs strictly for this patient
    rdvs = Rdv.query.filter_by(idPatient=int(user_id)).order_by(Rdv.dateRDV.asc(), Rdv.heureDebut.asc()).all()

    # Build appointments for template
    appointments = []
    # Try to fetch patient name
    patient_row = None
    try:
        patient_row = db.session.execute(text("SELECT nom, prenom FROM patient WHERE id_patient = :id"), {"id": int(user_id)}).mappings().first()
    except Exception:
        patient_row = None

    patient_name = (f"{patient_row['prenom']} {patient_row['nom']}" if patient_row else "Patient")
    start_lon = request.args.get('start_lon', type=float)
    start_lat = request.args.get('start_lat', type=float)
    patient_origin = (start_lon, start_lat) if None not in (start_lon, start_lat) else get_default_start_coords()

    city_coords = {
        'tunis': (10.10, 36.80),
        'ariana': (10.19, 36.86),
        'ben arous': (10.19, 36.75),
        'sousse': (10.64, 35.83),
    }

    def _destination_coords(location_value):
        if not location_value:
            return None
        location_text = str(location_value).strip().lower()
        for city_name, coords in city_coords.items():
            if city_name in location_text:
                return coords
        return city_coords['tunis']

    for r in rdvs:
        # try get doctor name
        person = None
        try:
            person = db.session.execute(text("SELECT nom, prenom FROM personnel_de_sante WHERE id_personnel = :id"), {"id": int(r.idPersonnel)}).mappings().first()
        except Exception:
            person = None

        doctor_name = (f"{person['prenom']} {person['nom']}" if person else "Médecin inconnu")

        # Default city/location; attempt to infer destination coordinates for traffic.
        city = 'Tunis'

        # Fetch weather via service (geocoding + forecast). Non-blocking for UX would be ideal,
        # but server-side we call synchronously and the template will render whatever we get.
        try:
            weather = get_weather(city)
        except Exception:
            weather = {"status": "error", "weather_recommendation": "Météo indisponible", "current_weather": {}}

        destination_coords = _destination_coords(getattr(r, 'lieu', None) if hasattr(r, 'lieu') else city)
        if destination_coords:
            traffic_notice = get_traffic_notice(patient_origin, destination_coords)
            optimal_departure = get_optimal_departure(patient_origin, destination_coords, city)
        else:
            traffic_notice = {
                'status': 'error',
                'recommendation': 'Information trafic indisponible',
                'duration_normal': None,
                'duration_current': None,
                'traffic_delay_percent': None,
            }
            optimal_departure = {
                'status': 'error',
                'recommendation': 'Information de départ indisponible',
                'base_duration': None,
                'traffic_duration': None,
                'weather_penalty': None,
                'traffic_penalty': None,
                'final_duration': None,
                'tone': 'normal',
            }

        appointments.append({
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'date': r.dateRDV.isoformat(),
            'time': r.heureDebut.strftime('%H:%M'),
            'location': getattr(r, 'lieu', 'Cabinet') if hasattr(r, 'lieu') else 'Cabinet',
            'weather': weather,
            'traffic_notice': traffic_notice,
            'optimal_departure': optimal_departure,
        })

    today = datetime.utcnow().date().isoformat()
    return render_template('appointments.html', appointments=appointments, today=today)


def _get_patient_row_by_cin(cin):
    with db.engine.connect() as conn:
        return conn.exec_driver_sql(
            """
            SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
            FROM patient
            WHERE telephone = %s
            LIMIT 1
            """,
            (str(cin).strip().lower(),),
        ).mappings().first()


def _patient_payload_from_row(row):
    if not row:
        return None

    return {
        "id": int(row["id_patient"]),
        "nom": row["nom"],
        "prenom": row["prenom"],
        "telephone": row["telephone"],
        "email": row.get("email") if hasattr(row, "get") else None,
        "cin": row.get("cin") if hasattr(row, "get") else None,
        "statut": 1,
        "statut_label": "patient",
    }


def _get_patient_health_fields(id_patient):
    patient_id = int(id_patient)
    result = {
        "dateNaissance": None,
        "age": None,
        "cin": None,
        "sexe": None,
        "allergies": [],
        "maladies": [],
    }

    _ensure_optional_user_columns()

    with db.engine.connect() as conn:
        existing_user_columns = {
            row[0]
            for row in conn.exec_driver_sql(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'user'
                                    AND COLUMN_NAME IN ('date_naissance', 'allergies', 'maladies', 'cin', 'sexe', 'sex', 'genre')
                """
            ).fetchall()
        }

        if existing_user_columns:
            select_columns = ", ".join([f"`{col}`" for col in sorted(existing_user_columns)])
            row = conn.exec_driver_sql(
                f"SELECT {select_columns} FROM user WHERE id = {patient_id} LIMIT 1"
            ).mappings().first()

            if row:
                date_naissance = row.get("date_naissance")
                if date_naissance:
                    result["dateNaissance"] = (
                        date_naissance.isoformat() if hasattr(date_naissance, "isoformat") else str(date_naissance)
                    )
                    result["age"] = _compute_age(date_naissance)

                result["allergies"] = _split_health_values(row.get("allergies"))
                result["maladies"] = _split_health_values(row.get("maladies"))

                cin_value = row.get("cin")
                if cin_value is not None and str(cin_value).strip():
                    result["cin"] = str(cin_value).strip()

                sexe_raw = row.get("sexe") or row.get("sex") or row.get("genre")
                if sexe_raw is not None and str(sexe_raw).strip():
                    result["sexe"] = str(sexe_raw).strip()

        rdv_age_column_exists = conn.exec_driver_sql(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'rdv'
              AND COLUMN_NAME = 'agePatient'
            """
        ).scalar() > 0

        if result["age"] is None and rdv_age_column_exists:
            age_row = conn.exec_driver_sql(
                f"""
                SELECT agePatient
                FROM rdv
                WHERE idPatient = {patient_id}
                  AND agePatient IS NOT NULL
                ORDER BY dateRDV DESC, heureDebut DESC
                LIMIT 1
                """
            ).first()
            if age_row and age_row[0] is not None:
                try:
                    result["age"] = int(age_row[0])
                except (TypeError, ValueError):
                    pass

    return result


def is_medical_staff(staff_id: int) -> bool:
    """Check if an ID belongs to medical staff in personnel_de_sante table."""
    if not staff_id or not isinstance(staff_id, int):
        return False
    try:
        with db.engine.connect() as conn:
            row = conn.exec_driver_sql(
                """
                SELECT id_personnel
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (staff_id,),
            ).mappings().first()
            return bool(row)
    except Exception:
        return False


def get_staff_category(staff_id: int) -> str:
    """Get staff category from personnel_de_sante table."""
    if not staff_id or not isinstance(staff_id, int):
        return "secretary"
    try:
        with db.engine.connect() as conn:
            row = conn.exec_driver_sql(
                """
                SELECT specialite
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (staff_id,),
            ).mappings().first()
            if row:
                specialite = (row["specialite"] or "").strip().lower()
                if specialite:
                    return "doctor"
    except Exception:
        return "secretary"
    return "secretary"


def is_doctor(staff_id: int) -> bool:
    """Check if staff member is a doctor (not a nurse)."""
    return is_medical_staff(staff_id) and get_staff_category(staff_id) == "doctor"


def _to_minutes(value):
    if isinstance(value, timedelta):
        return int(value.total_seconds() // 60)
    if isinstance(value, (int, float)):
        return int(value)
    return (value.hour * 60) + value.minute


def _to_hhmmss(total_minutes):
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}:00"


def refresh_db_status():
    global DB_READY
    try:
        db.session.execute(text("SELECT 1"))
        DB_READY = True
    except Exception:
        DB_READY = False
    return DB_READY


def _coerce_time_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.time()
    if hasattr(value, "hour") and hasattr(value, "minute") and hasattr(value, "second"):
        return value
    if isinstance(value, str):
        return parse_time(value)
    return None


def _coerce_minutes_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        minute_value = int(value)
        if 0 <= minute_value <= (24 * 60):
            return minute_value
        return None

    parsed_time = _coerce_time_value(value)
    if parsed_time is None:
        return None
    return _to_minutes(parsed_time)


def optimize_schedule(patients, doctor_schedule):
    """Optimize appointment start times with CP-SAT.

    Returns a list of dictionaries with patient_id, start, and end.
    Returns None when the model is infeasible or input validation fails.
    """
    if not isinstance(patients, list) or not isinstance(doctor_schedule, dict):
        return None

    doctor_start = _coerce_minutes_value(
        doctor_schedule.get("start_time") or doctor_schedule.get("start") or doctor_schedule.get("heure_debut")
    )
    doctor_end = _coerce_minutes_value(
        doctor_schedule.get("end_time") or doctor_schedule.get("end") or doctor_schedule.get("heure_fin")
    )

    if doctor_start is None or doctor_end is None:
        return None

    if doctor_end <= doctor_start:
        return None

    model = cp_model.CpModel()
    intervals = []
    start_vars = {}
    end_vars = {}
    waiting_vars = []

    for patient in patients:
        if not isinstance(patient, dict):
            return None

        patient_id = patient.get("id")
        if patient_id is None:
            patient_id = patient.get("patient_id")
        preferred_start = _coerce_minutes_value(
            patient.get("preferred_start_time")
            or patient.get("preferred_start")
            or patient.get("start")
            or patient.get("start_time")
        )
        preferred_end = _coerce_minutes_value(
            patient.get("preferred_end_time")
            or patient.get("preferred_end")
            or patient.get("end")
            or patient.get("end_time")
        )

        try:
            duration = int(patient.get("duration"))
        except (TypeError, ValueError):
            return None

        priority_value = patient.get("priority")
        if priority_value is None:
            priority_value = 1 if bool(patient.get("isUrgent", False)) else 0

        try:
            priority = int(priority_value)
        except (TypeError, ValueError):
            return None

        if priority < 0:
            return None

        if patient_id is None or preferred_start is None or preferred_end is None or duration <= 0:
            return None

        latest_start_by_patient = preferred_end - duration
        latest_start_by_doctor = doctor_end - duration
        earliest_start = max(preferred_start, doctor_start)
        latest_start = min(latest_start_by_patient, latest_start_by_doctor)

        if earliest_start > latest_start:
            return None

        start_var = model.NewIntVar(earliest_start, latest_start, f"start_{patient_id}")
        end_var = model.NewIntVar(earliest_start + duration, latest_start + duration, f"end_{patient_id}")
        model.Add(end_var == start_var + duration)

        # Add one interval per patient and enforce no overlap globally.
        interval_var = model.NewIntervalVar(start_var, duration, end_var, f"interval_{patient_id}")
        waiting_var = model.NewIntVar(0, doctor_end - doctor_start, f"waiting_{patient_id}")
        model.Add(waiting_var == start_var - preferred_start)

        intervals.append(interval_var)
        start_vars[patient_id] = start_var
        end_vars[patient_id] = end_var
        priority_weight = max(1, priority)
        if bool(patient.get("isUrgent", False)):
            priority_weight = max(priority_weight, 1000)
        waiting_vars.append(waiting_var * priority_weight)

    if not intervals:
        return []

    model.AddNoOverlap(intervals)
    model.Minimize(sum(waiting_vars))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)
    print(f"[OR-TOOLS] solver status: {solver.StatusName(status)}")
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    print(f"[OR-TOOLS] objective value: {solver.ObjectiveValue()}")

    optimized_schedule = []
    for patient in patients:
        patient_id = patient.get("id")
        if patient_id is None:
            patient_id = patient.get("patient_id")
        start_minute = solver.Value(start_vars[patient_id])
        end_minute = solver.Value(end_vars[patient_id])
        optimized_schedule.append(
            {
                "patient_id": patient_id,
                "start": start_minute,
                "end": end_minute,
            }
        )
        print(f"[OR-TOOLS] appointment patient={patient_id} start={start_minute} end={end_minute}")

    optimized_schedule.sort(key=lambda item: item["start"])
    return optimized_schedule

def optimize_full_day(patients, start_window, end_window):
    if not isinstance(patients, list):
        return None
    window_start = _coerce_minutes_value(start_window)
    window_end = _coerce_minutes_value(end_window)
    if window_start is None or window_end is None or window_end <= window_start:
        return None
    normalized = []
    for p in patients:
        if not isinstance(p, dict) or "id" not in p:
            return None
        dur = _coerce_minutes_value(p.get("duration") or p.get("duree"))
        if dur is None or dur <= 0:
            return None
        normalized.append({"id": p["id"], "duration": int(dur)})
    model = cp_model.CpModel()
    starts, intervals = [], []
    for i, p in enumerate(normalized):
        max_start = window_end - p["duration"]
        if max_start < window_start:
            return None
        s = model.NewIntVar(window_start, max_start, f"s_{i}")
        e = model.NewIntVar(window_start + p["duration"], window_end, f"e_{i}")
        model.Add(e == s + p["duration"])
        interval = model.NewIntervalVar(s, p["duration"], e, f"int_{i}")
        starts.append(s)
        intervals.append(interval)
    model.AddNoOverlap(intervals)
    gaps = []
    for i in range(len(starts) - 1):
        gap = model.NewIntVar(0, window_end - window_start, f"gap_{i}")
        model.Add(gap == starts[i + 1] - (starts[i] + normalized[i]["duration"]))
        gaps.append(gap)
    if gaps:
        model.Minimize(sum(gaps))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    result = []
    for i, p in enumerate(normalized):
        start_min = int(solver.Value(starts[i]))
        end_min = start_min + p["duration"]
        result.append({"patientId": p["id"], "heureDebut": _to_hhmmss(start_min), "heureFin": _to_hhmmss(end_min)})
    return result


def optimize_day_with_absence(existing_rdvs, day_start, day_end, absence_start, absence_end):
    """Apply a strict delay around a short absence window.

    Business rule: if absence is N hours, impacted appointments are delayed by N hours.
    """
    if not isinstance(existing_rdvs, list):
        return None

    window_start = _coerce_minutes_value(day_start)
    window_end = _coerce_minutes_value(day_end)
    blocked_start = _coerce_minutes_value(absence_start)
    blocked_end = _coerce_minutes_value(absence_end)

    if None in (window_start, window_end, blocked_start, blocked_end):
        return None

    if window_end <= window_start or blocked_end <= blocked_start:
        return None

    if blocked_start < window_start or blocked_end > window_end:
        return None

    blocked_duration = blocked_end - blocked_start

    normalized = []
    for index, rdv in enumerate(existing_rdvs):
        if not isinstance(rdv, dict):
            return None

        rdv_id = rdv.get("id") or rdv.get("idRdv") or rdv.get("idRDV")
        if rdv_id is None:
            rdv_id = index

        start = _coerce_minutes_value(rdv.get("start") or rdv.get("heureDebut"))
        duration = _coerce_minutes_value(rdv.get("duration") or rdv.get("duree"))
        if start is None or duration is None or duration <= 0:
            return None

        normalized.append({"id": rdv_id, "start": int(start), "duration": int(duration)})

    if not normalized:
        return []

    normalized.sort(key=lambda value: value["start"])

    optimized_plan = []
    previous_end = window_start
    for rdv in normalized:
        old_start = rdv["start"]
        duration = rdv["duration"]
        old_end = old_start + duration

        in_absence_scope = old_start < blocked_end and old_end > blocked_start
        after_absence_in_day = old_start >= blocked_end
        requested_start = old_start + blocked_duration if (in_absence_scope or after_absence_in_day) else old_start

        # Keep a valid chronological planning after shifting.
        new_start = max(requested_start, previous_end)
        new_end = new_start + duration

        if new_end > (24 * 60):
            return None

        optimized_plan.append(
            {
                "id": rdv["id"],
                "heureDebut": _to_hhmmss(new_start),
                "heureFin": _to_hhmmss(new_end),
                "old_start": old_start,
                "new_start": new_start,
                "new_end": new_end,
            }
        )
        previous_end = new_end

    return optimized_plan


def schedule_with_emergency(existing_rdvs, duration, start_window, end_window):
    if not isinstance(existing_rdvs, list):
        return None
    urgent_duration = _coerce_minutes_value(duration)
    window_start = _coerce_minutes_value(start_window)
    window_end = _coerce_minutes_value(end_window)
    if urgent_duration is None or window_start is None or window_end is None:
        return None
    if urgent_duration <= 0 or window_end <= window_start:
        return None
    model = cp_model.CpModel()
    starts, intervals, shifts, normalized_rdvs = [], [], [], []
    moved_flags = []
    for index, rdv in enumerate(existing_rdvs):
        if not isinstance(rdv, dict):
            return None
        rdv_id = rdv.get("id") or rdv.get("idRdv") or index
        rdv_start = _coerce_minutes_value(rdv.get("start") or rdv.get("heureDebut"))
        rdv_duration = _coerce_minutes_value(rdv.get("duration") or rdv.get("duree"))
        if rdv_start is None or rdv_duration is None or rdv_duration <= 0:
            return None
        latest_start = window_end - rdv_duration
        if latest_start < window_start:
            return None
        s = model.NewIntVar(window_start, latest_start, f"s_{index}")
        e = model.NewIntVar(window_start + rdv_duration, window_end, f"e_{index}")
        model.Add(e == s + rdv_duration)
        interval = model.NewIntervalVar(s, rdv_duration, e, f"int_{index}")
        shift = model.NewIntVar(0, window_end - window_start, f"shift_{index}")
        model.AddAbsEquality(shift, s - rdv_start)
        moved = model.NewBoolVar(f"moved_{index}")
        model.Add(shift == 0).OnlyEnforceIf(moved.Not())
        model.Add(shift >= 1).OnlyEnforceIf(moved)
        starts.append(s)
        intervals.append(interval)
        shifts.append(shift)
        moved_flags.append(moved)
        normalized_rdvs.append({"id": rdv_id, "start": rdv_start, "duration": rdv_duration})
    u_start = model.NewIntVar(window_start, window_end - urgent_duration, "u_start")
    u_end = model.NewIntVar(window_start + urgent_duration, window_end, "u_end")
    model.Add(u_end == u_start + urgent_duration)
    u_interval = model.NewIntervalVar(u_start, urgent_duration, u_end, "u_int")
    model.AddNoOverlap(intervals + [u_interval])

    # Lexicographic-like objective: place the urgent patient as early as possible,
    # then minimize the number of displaced RDVs, then minimize the displacement size.
    planning_span = max(1, window_end - window_start)
    max_shift_penalty = planning_span * max(1, len(normalized_rdvs))
    urgent_weight = max_shift_penalty * 1000 + 1
    move_weight = planning_span * 10
    model.Minimize(
        (u_start * urgent_weight)
        + (sum(moved_flags) * move_weight if moved_flags else 0)
        + (sum(shifts) if shifts else 0)
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    updated = []
    for i, rdv in enumerate(normalized_rdvs):
        new_start = solver.Value(starts[i])
        new_end = new_start + rdv["duration"]
        updated.append({
            "id": rdv["id"],
            "old_start": rdv["start"],
            "new_start": new_start,
            "new_end": new_end,
            "moved": new_start != rdv["start"],
        })

    updated.sort(key=lambda item: (item["new_start"], item["id"]))
    optimized_plan = [
        {
            "id": item["id"],
            "heureDebut": _to_hhmmss(item["new_start"]),
            "heureFin": _to_hhmmss(item["new_end"]),
            "old_start": item["old_start"],
            "new_start": item["new_start"],
            "new_end": item["new_end"],
            "moved": item["moved"],
            "isUrgent": False,
        }
        for item in updated
    ]
    optimized_plan.append(
        {
            "id": "urgent",
            "heureDebut": _to_hhmmss(solver.Value(u_start)),
            "heureFin": _to_hhmmss(solver.Value(u_end)),
            "old_start": None,
            "new_start": solver.Value(u_start),
            "new_end": solver.Value(u_end),
            "moved": False,
            "isUrgent": True,
        }
    )
    optimized_plan.sort(key=lambda item: (item["new_start"], 1 if item.get("isUrgent") else 0, item["id"]))

    return {
        "urgent_start": solver.Value(u_start),
        "urgent_end": solver.Value(u_end),
        "updated": updated,
        "optimized_plan": optimized_plan,
    }


def _get_doctor_planning_window(id_personnel, date_rdv):
    """Return the effective working window for a doctor on a given day."""
    plannings = (
        Planning.query
        .filter_by(idPersonnel=id_personnel, date=date_rdv)
        .order_by(Planning.heure_debut.asc())
        .all()
    )

    if plannings:
        window_start = min(_to_minutes(plan.heure_debut) for plan in plannings)
        window_end = max(_to_minutes(plan.heure_fin) for plan in plannings)
        return window_start, window_end, plannings, False

    return 9 * 60, 17 * 60, [], True


def _get_doctor_rdvs_for_day(id_personnel, date_rdv):
    """Load all appointments for one doctor and one date in chronological order."""
    return (
        Rdv.query
        .filter_by(idPersonnel=id_personnel, dateRDV=date_rdv)
        .order_by(Rdv.heureDebut.asc())
        .all()
    )


def _build_rdv_snapshot(rdv):
    return {
        "id": rdv.idRdv,
        "start": _to_minutes(rdv.heureDebut),
        "duration": _to_minutes(rdv.heureFin) - _to_minutes(rdv.heureDebut),
        "patientId": rdv.idPatient,
    }


def _find_immediate_urgent_slot(existing_rdvs, duration, window_start, window_end, reference_minute=None):
    """Return a free slot for an urgent appointment without moving any RDV."""
    urgent_duration = _coerce_minutes_value(duration)
    window_start = _coerce_minutes_value(window_start)
    window_end = _coerce_minutes_value(window_end)
    reference_minute = _coerce_minutes_value(reference_minute)

    if urgent_duration is None or window_start is None or window_end is None:
        return None
    if urgent_duration <= 0 or window_end <= window_start:
        return None

    cursor = max(window_start, reference_minute if reference_minute is not None else window_start)
    if cursor + urgent_duration > window_end:
        return None

    ordered_rdvs = []
    for index, rdv in enumerate(existing_rdvs or []):
        if not isinstance(rdv, dict):
            continue
        rdv_start = _coerce_minutes_value(rdv.get("start") or rdv.get("heureDebut"))
        rdv_duration = _coerce_minutes_value(rdv.get("duration") or rdv.get("duree"))
        if rdv_start is None or rdv_duration is None or rdv_duration <= 0:
            continue
        ordered_rdvs.append((rdv_start, rdv_start + rdv_duration, rdv.get("id") or rdv.get("idRdv") or index))

    ordered_rdvs.sort(key=lambda item: item[0])

    for rdv_start, rdv_end, _ in ordered_rdvs:
        if cursor + urgent_duration <= rdv_start:
            return {
                "urgent_start": cursor,
                "urgent_end": cursor + urgent_duration,
                "updated": [],
                "optimized_plan": [
                    {
                        "id": "urgent",
                        "heureDebut": _to_hhmmss(cursor),
                        "heureFin": _to_hhmmss(cursor + urgent_duration),
                        "old_start": None,
                        "new_start": cursor,
                        "new_end": cursor + urgent_duration,
                        "moved": False,
                        "isUrgent": True,
                    }
                ],
                "mode": "immediate",
            }
        cursor = max(cursor, rdv_end)
        if cursor + urgent_duration > window_end:
            return None

    if cursor + urgent_duration <= window_end:
        return {
            "urgent_start": cursor,
            "urgent_end": cursor + urgent_duration,
            "updated": [],
            "optimized_plan": [
                {
                    "id": "urgent",
                    "heureDebut": _to_hhmmss(cursor),
                    "heureFin": _to_hhmmss(cursor + urgent_duration),
                    "old_start": None,
                    "new_start": cursor,
                    "new_end": cursor + urgent_duration,
                    "moved": False,
                    "isUrgent": True,
                }
            ],
            "mode": "immediate",
        }

    return None


def _apply_rescheduled_appointments(id_personnel, date_rdv, result):
    """Persist the optimized urgent slot and the shifted appointments."""
    urgent_start = parse_time(_to_hhmmss(result["urgent_start"]))
    urgent_end = parse_time(_to_hhmmss(result["urgent_end"]))

    if urgent_start is None or urgent_end is None:
        return None

    rdv_rows = {
        rdv.idRdv: rdv
        for rdv in Rdv.query.filter_by(idPersonnel=id_personnel, dateRDV=date_rdv).all()
    }

    updated_rows = []
    for item in result.get("updated", []):
        rdv = rdv_rows.get(item.get("id"))
        if not rdv:
            continue
        rdv.heureDebut = parse_time(_to_hhmmss(int(item["new_start"])))
        rdv.heureFin = parse_time(_to_hhmmss(int(item["new_end"])))
        updated_rows.append({
            "id": rdv.idRdv,
            "heureDebut": _format_time_for_client(rdv.heureDebut),
            "heureFin": _format_time_for_client(rdv.heureFin),
            "idPatient": rdv.idPatient,
            "idPersonnel": rdv.idPersonnel,
            "statut": "Confirme",
        })

    return {
        "urgent_start": urgent_start,
        "urgent_end": urgent_end,
        "updated_rows": updated_rows,
    }


def _apply_optimized_day_plan(id_personnel, date_rdv, optimized_plan):
    """Persist an optimized day plan returned by optimize_full_day."""
    if not isinstance(optimized_plan, list):
        return None

    rdv_rows = {
        rdv.idRdv: rdv
        for rdv in Rdv.query.filter_by(idPersonnel=id_personnel, dateRDV=date_rdv).all()
    }

    updated_rows = []
    for item in optimized_plan:
        if not isinstance(item, dict):
            continue

        rdv_id = item.get("id") or item.get("idRdv") or item.get("idRDV") or item.get("patientId")
        try:
            rdv_id = int(rdv_id)
        except (TypeError, ValueError):
            continue

        rdv = rdv_rows.get(rdv_id)
        if not rdv:
            continue

        heure_debut = parse_time(item.get("heureDebut") or _to_hhmmss(item.get("start")))
        heure_fin = parse_time(item.get("heureFin") or _to_hhmmss(item.get("end")))
        if heure_debut is None or heure_fin is None:
            continue

        previous_start = _to_minutes(rdv.heureDebut)
        previous_end = _to_minutes(rdv.heureFin)
        next_start = _to_minutes(heure_debut)
        next_end = _to_minutes(heure_fin)

        # Keep previous times for notification payload before overwriting.
        previous_start_str = _format_time_for_client(rdv.heureDebut)
        previous_end_str = _format_time_for_client(rdv.heureFin)

        rdv.heureDebut = heure_debut
        rdv.heureFin = heure_fin

        updated_rows.append(
            {
                "id": rdv.idRdv,
                "heureDebut": _format_time_for_client(rdv.heureDebut),
                "heureFin": _format_time_for_client(rdv.heureFin),
                "idPatient": rdv.idPatient,
                "idPersonnel": rdv.idPersonnel,
                "statut": "Confirme",
                "previousHeureDebut": previous_start_str,
                "previousHeureFin": previous_end_str,
            }
        )

    return updated_rows



def check_appointment_conflict(idPersonnel, dateRDV, heureDebut, heureFin):
    """
    Check if the requested time slot conflicts with existing appointments.
    Returns (has_conflict, conflicting_appointment) tuple.
    """
    existing_rdvs = (
        Rdv.query
        .filter_by(idPersonnel=idPersonnel, dateRDV=dateRDV)
        .all()
    )
    
    new_start_min = _to_minutes(heureDebut)
    new_end_min = _to_minutes(heureFin)
    
    for rdv in existing_rdvs:
        existing_start_min = _to_minutes(rdv.heureDebut)
        existing_end_min = _to_minutes(rdv.heureFin)
        
        # Check for overlap: new slot starts before existing ends AND new slot ends after existing starts
        if new_start_min < existing_end_min and new_end_min > existing_start_min:
            return (True, rdv)
    
    return (False, None)


def _build_available_slots_for_doctor(id_personnel, date_rdv, slot_duration=30, single_proposal=False, proposal_index=0):
    """Build the slot candidates used by OR-Tools suggestions for one doctor/day."""
    slot_duration = _coerce_minutes_value(slot_duration) or 30
    if slot_duration <= 0:
        slot_duration = 30

    plannings = (
        Planning.query
        .filter_by(idPersonnel=id_personnel, date=date_rdv)
        .order_by(Planning.heure_debut.asc())
        .all()
    )

    with db.engine.connect() as conn:
        appointment_rows = conn.exec_driver_sql(
            """
            SELECT idRDV, heureDebut, heureFin
            FROM rdv
            WHERE idPersonnel = %s AND dateRDV = %s
            ORDER BY heureDebut ASC
            """,
            (id_personnel, date_rdv),
        ).mappings().all()

    appointments = [
        {
            "idRdv": row["idRDV"],
            "heureDebut": row["heureDebut"],
            "heureFin": row["heureFin"],
        }
        for row in appointment_rows
    ]

    booked_ranges = [(_to_minutes(r["heureDebut"]), _to_minutes(r["heureFin"])) for r in appointments]

    planning_ranges = [(_to_minutes(plan.heure_debut), _to_minutes(plan.heure_fin)) for plan in plannings]
    used_default_planning = False
    if not planning_ranges:
        planning_ranges = [(9 * 60, 17 * 60)]
        used_default_planning = True

    suggested_slots = []
    for start_min, end_min in planning_ranges:
        if end_min <= start_min:
            continue

        cursor = start_min
        while cursor + slot_duration <= end_min:
            slot_start = cursor
            slot_end = cursor + slot_duration
            overlaps = any(slot_start < booked_end and slot_end > booked_start for booked_start, booked_end in booked_ranges)
            if not overlaps:
                suggested_slots.append({"heureDebut": _to_hhmmss(slot_start), "heureFin": _to_hhmmss(slot_end)})
            cursor += slot_duration

    optimized_suggested_slots = None
    try:
        normalized = []
        for r in appointments:
            if r.get("heureDebut") is None or r.get("heureFin") is None:
                continue
            dur = _to_minutes(r["heureFin"]) - _to_minutes(r["heureDebut"])
            if dur <= 0:
                continue
            normalized.append({"id": r.get("idRdv"), "duration": dur})

        earliest_booked_start = min((start for start, _ in booked_ranges), default=None)
        latest_booked_end = max((end for _, end in booked_ranges), default=None)
        overall_start = min(start for start, _ in planning_ranges)
        overall_end = max(end for _, end in planning_ranges)
        if earliest_booked_start is not None:
            overall_start = min(overall_start, earliest_booked_start)
        if latest_booked_end is not None:
            overall_end = max(overall_end, latest_booked_end)

        if normalized:
            compact = optimize_full_day(normalized, overall_start, overall_end)
            if compact:
                opt_booked = []
                for ap in compact:
                    tstart = parse_time(ap.get("heureDebut"))
                    tend = parse_time(ap.get("heureFin"))
                    if tstart is None or tend is None:
                        continue
                    opt_booked.append((_to_minutes(tstart), _to_minutes(tend)))

                opt_slots = []
                for start_min, end_min in planning_ranges:
                    if end_min <= start_min:
                        continue
                    cursor = start_min
                    while cursor + slot_duration <= end_min:
                        slot_start = cursor
                        slot_end = cursor + slot_duration
                        overlaps_opt = any(slot_start < booked_end and slot_end > booked_start for booked_start, booked_end in opt_booked)
                        if not overlaps_opt:
                            opt_slots.append({"heureDebut": _to_hhmmss(slot_start), "heureFin": _to_hhmmss(slot_end)})
                        cursor += slot_duration
                optimized_suggested_slots = opt_slots
    except Exception:
        optimized_suggested_slots = None

    if single_proposal:
        candidate_slots = optimized_suggested_slots or suggested_slots
        if candidate_slots:
            selected_slot = candidate_slots[proposal_index % len(candidate_slots)]
            suggested_slots = [selected_slot]
            optimized_suggested_slots = [selected_slot] if optimized_suggested_slots else None

    return {
        "suggestedSlots": suggested_slots,
        "optimizedSuggestedSlots": optimized_suggested_slots,
        "planningSource": "default" if used_default_planning else "planning",
        "slotDuration": slot_duration,
    }


def normalize_access_code(value: str) -> str:
    return "".join(str(value or "").strip().split()).lower()


TEST_ACCESS_CODE_ALIASES = {"med2026", "staff2026"}


def role_to_auth_role(statut: int) -> str:
    return "medical_staff" if statut == 2 else "patient"


def create_jwt_token(user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "user_type": role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _get_authenticated_patient_id():
    auth_header = request.headers.get("Authorization", "")
    try:
        preview = (auth_header or "")[:100]
        print(f"[auth] path={request.path} Authorization={preview}", flush=True)
    except Exception:
        pass
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"access": False, "message": "Token manquant ou invalide"}), 401)

    token = auth_header[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None, (jsonify({"access": False, "message": "Token invalide"}), 401)

    patient_id = payload.get("user_id")
    if payload.get("role") != "patient" or not patient_id:
        return None, (jsonify({"access": False, "message": "Acces refuse - patient seulement"}), 403)

    return int(patient_id), None


def _format_time_for_client(value):
    return _format_sql_time(value, "%H:%M")


def _normalize_sql_time(value):
    if value is None:
        return None

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds()) % (24 * 3600)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return datetime.min.replace(hour=hours, minute=minutes, second=seconds).time()

    if hasattr(value, "hour") and hasattr(value, "minute") and hasattr(value, "second"):
        return value

    value_str = str(value).strip()
    if not value_str:
        return None

    parts = value_str.split(":")
    if len(parts) < 2:
        return None


def _format_sql_time(value, format_string="%H:%M:%S"):
    normalized = _normalize_sql_time(value)
    if normalized is None:
        return None

    return normalized.strftime(format_string)

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) > 2 else 0
        return datetime.min.replace(hour=hours, minute=minutes, second=seconds).time()
    except ValueError:
        return None


def _resolve_patient_doctor_status(patient_id, selected_date):
    with db.engine.connect() as conn:
        patient_rdvs = conn.exec_driver_sql(
            """
            SELECT
                r.idRDV AS id,
                r.idPersonnel,
                r.dateRDV,
                r.heureDebut,
                r.heureFin
            FROM rdv r
            WHERE r.idPatient = %s
              AND r.dateRDV = %s
            ORDER BY r.heureDebut ASC
            """,
            (patient_id, selected_date),
        ).mappings().all()

        if not patient_rdvs:
            return None

        current_time = datetime.utcnow().time()
        current_appointment = None
        for rdv in patient_rdvs:
            start_time = _normalize_sql_time(rdv["heureDebut"])
            end_time = _normalize_sql_time(rdv["heureFin"])
            if start_time and end_time and start_time <= current_time < end_time:
                current_appointment = rdv
                break

        selected_appointment = current_appointment or patient_rdvs[0]
        doctor_id = selected_appointment["idPersonnel"]

        doctor_rdvs = conn.exec_driver_sql(
            """
            SELECT
                r.idRDV AS id,
                r.idPatient,
                r.heureDebut,
                r.heureFin
            FROM rdv r
            WHERE r.idPersonnel = %s
              AND r.dateRDV = %s
            ORDER BY r.heureDebut ASC
            """,
            (doctor_id, selected_date),
        ).mappings().all()

    doctor_status = "disponible"
    for rdv in doctor_rdvs:
        start_time = _normalize_sql_time(rdv["heureDebut"])
        end_time = _normalize_sql_time(rdv["heureFin"])
        if start_time and end_time and start_time <= current_time < end_time:
            doctor_status = "en consultation" if int(rdv["idPatient"]) == int(patient_id) else "occupied"
            break

    # Compute basic queue statistics for the doctor today
    total_patients = len(doctor_rdvs)
    patients_waiting = 0
    wait_time_minutes = 0

    # Build an OR-Tools friendly view of today's queue to estimate waiting time.
    ortools_patients = []
    selected_appointment_id = int(selected_appointment["id"])
    selected_appointment_start = _normalize_sql_time(selected_appointment["heureDebut"])

    for rdv in doctor_rdvs:
        start_time = _normalize_sql_time(rdv["heureDebut"])
        end_time = _normalize_sql_time(rdv["heureFin"])
        if start_time is None or end_time is None:
            continue

        start_minutes = _to_minutes(start_time)
        end_minutes = _to_minutes(end_time)
        duration_minutes = max(1, end_minutes - start_minutes)
        ortools_patients.append(
            {
                "id": int(rdv["id"]),
                "start": start_minutes,
                "end": end_minutes,
                "duration": duration_minutes,
                "priority": 1000 if int(rdv["idPatient"]) == int(patient_id) else 1,
                "isUrgent": False,
            }
        )

    doctor_schedule = {
        "start": _to_minutes(_normalize_sql_time(doctor_rdvs[0]["heureDebut"])) if doctor_rdvs else _to_minutes(selected_appointment_start),
        "end": _to_minutes(_normalize_sql_time(doctor_rdvs[-1]["heureFin"])) if doctor_rdvs else _to_minutes(selected_appointment_start),
    }

    optimized_wait_time = None
    if ortools_patients and doctor_schedule["start"] is not None and doctor_schedule["end"] is not None:
        try:
            optimized_plan = optimize_schedule(ortools_patients, doctor_schedule)
            if optimized_plan:
                optimized_map = {int(item["patient_id"]): int(item["start"]) for item in optimized_plan}
                optimized_start = optimized_map.get(selected_appointment_id)
                if optimized_start is not None:
                    now_minutes = _to_minutes(current_time)
                    optimized_wait_time = max(0, optimized_start - now_minutes)
        except Exception:
            optimized_wait_time = None

    # Count patients with appointments later than now
    for rdv in doctor_rdvs:
        start_time = _normalize_sql_time(rdv["heureDebut"])
        if start_time and start_time > current_time:
            patients_waiting += 1

    # Prefer the OR-Tools estimate; fall back to a direct time difference if needed.
    if optimized_wait_time is not None:
        wait_time_minutes = int(optimized_wait_time)
    else:
        selected_start = _normalize_sql_time(selected_appointment["heureDebut"])
        if selected_start and selected_start > current_time:
            today_dt = datetime.combine(selected_date, selected_start)
            now_dt = datetime.combine(selected_date, current_time)
            delta = today_dt - now_dt
            wait_time_minutes = int(delta.total_seconds() // 60)
        else:
            wait_time_minutes = 0

    return {
        "access": True,
        "doctor_status": doctor_status,
        "your_appointment_time": _format_time_for_client(selected_appointment["heureDebut"]),
        "totalPatients": int(total_patients),
        "patientsWaiting": int(patients_waiting),
        "waitTime": int(wait_time_minutes),
    }


def migrate_mysql_schema():
    """Ensure MySQL schema matches models and foreign keys are enforced."""
    try:
        with db.engine.begin() as conn:
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS personnel_de_sante (
                    id_personnel INT NOT NULL AUTO_INCREMENT,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    specialite VARCHAR(120) NULL,
                    region VARCHAR(120) NULL,
                    disponibilite TINYINT(1) NOT NULL DEFAULT 1,
                    PRIMARY KEY (id_personnel)
                ) ENGINE=InnoDB
                """
            )

            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS patient (
                    id_patient INT NOT NULL AUTO_INCREMENT,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    telephone VARCHAR(30) NULL,
                    adresse VARCHAR(255) NULL,
                    PRIMARY KEY (id_patient)
                ) ENGINE=InnoDB
                """
            )

            for column_name in ("email", "cin", "password"):
                try:
                    conn.exec_driver_sql(f"ALTER TABLE patient DROP COLUMN IF EXISTS `{column_name}`")
                except Exception:
                    pass

            conn.exec_driver_sql(
                """
                INSERT INTO patient (id_patient, nom, prenom, telephone)
                SELECT id, nom, prenom, telephone
                FROM user
                WHERE role = 1
                ON DUPLICATE KEY UPDATE
                    nom = VALUES(nom),
                    prenom = VALUES(prenom),
                    telephone = VALUES(telephone)
                """
            )

            # Create canonical `user` table if missing.
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS user (
                    id INT NOT NULL AUTO_INCREMENT,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    telephone VARCHAR(30) NULL,
                    email VARCHAR(120) NULL,
                    role INT NOT NULL,
                    specialite VARCHAR(120) NULL,
                    region VARCHAR(120) NULL,
                    disponibilite VARCHAR(255) NULL,
                    password VARCHAR(255) NOT NULL DEFAULT '',
                    access_code VARCHAR(120) NULL,
                    PRIMARY KEY (id),
                    UNIQUE KEY uq_user_email (email),
                    UNIQUE KEY uq_user_access_code (access_code)
                ) ENGINE=InnoDB
                """
            )

            # Ensure required columns exist even when `user` table already existed.
            for col_def in [
                "email VARCHAR(120) NULL",
                "specialite VARCHAR(120) NULL",
                "password VARCHAR(255) NOT NULL DEFAULT ''",
                "access_code VARCHAR(120) NULL",
                "role INT NULL"
            ]:
                col_name = col_def.split()[0]
                try:
                    conn.exec_driver_sql(f"ALTER TABLE user ADD COLUMN {col_def}")
                except Exception:
                    pass

            statut_exists = conn.exec_driver_sql(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'user'
                  AND COLUMN_NAME = 'statut'
                """
            ).scalar() > 0

            if statut_exists:
                conn.exec_driver_sql("UPDATE user SET role = COALESCE(role, statut, 1)")
            else:
                conn.exec_driver_sql("UPDATE user SET role = COALESCE(role, 1)")

            conn.exec_driver_sql("ALTER TABLE user MODIFY COLUMN role INT NOT NULL")
            conn.exec_driver_sql("ALTER TABLE user ADD UNIQUE INDEX IF NOT EXISTS uq_user_email (email)")
            conn.exec_driver_sql("ALTER TABLE user ADD UNIQUE INDEX IF NOT EXISTS uq_user_access_code (access_code)")

            # Seed a default test access code for one medical staff account if missing.
            default_code_exists = conn.exec_driver_sql(
                "SELECT COUNT(*) FROM user WHERE role = 2 AND access_code = 'STAFF2026'"
            ).scalar() > 0
            if not default_code_exists:
                conn.exec_driver_sql(
                    """
                    UPDATE user
                    SET access_code = 'STAFF2026'
                    WHERE role = 2 AND (access_code IS NULL OR access_code = '' OR access_code = 'MED2026')
                    LIMIT 1
                    """
                )

            # If legacy `users` table exists, copy rows into new `user` table.
            users_exists = conn.exec_driver_sql("SHOW TABLES LIKE 'users'").fetchone() is not None
            if users_exists:
                conn.exec_driver_sql(
                    """
                    INSERT INTO user (id, nom, prenom, telephone, email, role, specialite, disponibilite, password)
                    SELECT id, nom, prenom, telephone, email, role, specialite, disponibilite, password
                    FROM users
                    ON DUPLICATE KEY UPDATE
                        nom = VALUES(nom),
                        prenom = VALUES(prenom),
                        telephone = VALUES(telephone),
                        email = VALUES(email),
                        role = VALUES(role),
                        specialite = VALUES(specialite),
                        disponibilite = VALUES(disponibilite),
                        password = VALUES(password)
                    """
                )

            # Add missing column in planning if needed.
            conn.exec_driver_sql(
                "ALTER TABLE planning ADD COLUMN IF NOT EXISTS duree_creneau INT NOT NULL DEFAULT 30"
            )

            # Make rdv primary key auto increment to avoid duplicate key insert errors.
            conn.exec_driver_sql(
                "ALTER TABLE rdv MODIFY COLUMN idRDV INT NOT NULL AUTO_INCREMENT"
            )

            # Drop old access_codes table if still present.
            conn.exec_driver_sql("DROP TABLE IF EXISTS access_codes")

            # Drop existing FK constraints to rebind them to `user`.
            fk_names_rows = conn.exec_driver_sql(
                """
                SELECT TABLE_NAME, CONSTRAINT_NAME
                FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND CONSTRAINT_TYPE = 'FOREIGN KEY'
                  AND TABLE_NAME IN ('rdv', 'planning')
                """
            ).fetchall()
            for table_name, constraint_name in fk_names_rows:
                conn.exec_driver_sql(
                    f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}"
                )

            # Remove orphan rows before adding FK constraints.
            conn.exec_driver_sql(
                "DELETE r FROM rdv r LEFT JOIN patient p ON r.idPatient = p.id_patient WHERE r.idPatient IS NOT NULL AND p.id_patient IS NULL"
            )
            conn.exec_driver_sql(
                "DELETE r FROM rdv r LEFT JOIN personnel_de_sante ps ON r.idPersonnel = ps.id_personnel WHERE r.idPersonnel IS NOT NULL AND ps.id_personnel IS NULL"
            )
            conn.exec_driver_sql(
                "DELETE p FROM planning p LEFT JOIN personnel_de_sante ps ON p.idPersonnel = ps.id_personnel WHERE p.idPersonnel IS NOT NULL AND ps.id_personnel IS NULL"
            )

            # Recreate FK constraints against `patient` and `personnel_de_sante`.
            conn.exec_driver_sql(
                "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_patient FOREIGN KEY (idPatient) REFERENCES patient(id_patient) ON UPDATE CASCADE ON DELETE RESTRICT"
            )
            conn.exec_driver_sql(
                "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_personnel FOREIGN KEY (idPersonnel) REFERENCES personnel_de_sante(id_personnel) ON UPDATE CASCADE ON DELETE RESTRICT"
            )
            conn.exec_driver_sql(
                "ALTER TABLE planning ADD CONSTRAINT fk_planning_personnel FOREIGN KEY (idPersonnel) REFERENCES personnel_de_sante(id_personnel) ON UPDATE CASCADE ON DELETE RESTRICT"
            )

            # Drop user table now that all data has been migrated.
            conn.exec_driver_sql("DROP TABLE IF EXISTS users")
            conn.exec_driver_sql("DROP TABLE IF EXISTS user")
    except Exception as exc:
        print(f"Migration MySQL warning: {exc}")


@app.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json() or {}

        nom = data.get("nom")
        prenom = data.get("prenom")
        statut = data.get("statut", 1)
        telephone = data.get("telephone")
        email = data.get("email")
        specialite = data.get("specialite")
        disponibilite = data.get("disponibilite")
        password = data.get("password", "")
        access_code = data.get("accessCode") or data.get("access_code")

        if not nom or not prenom:
            return jsonify({"error": "nom et prenom sont obligatoires"}), 400

        try:
            statut = int(statut)
        except (TypeError, ValueError):
            return jsonify({"error": "statut invalide (1=patient, 2=personnel medical)"}), 400

        if statut not in USER_STATUS:
            return jsonify({"error": "statut invalide (1=patient, 2=personnel medical)"}), 400

        if statut == 2 and not specialite:
            return jsonify({"error": "specialite est obligatoire pour le personnel medical"}), 400

        if statut == 2 and not access_code:
            return jsonify({"error": "accessCode est obligatoire pour le personnel medical"}), 400

        if statut == 1:
            _ensure_patient_table_columns()
            with db.engine.begin() as conn:
                existing = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE telephone = %s
                    LIMIT 1
                    """,
                    (telephone,),
                ).mappings().first()

                if existing:
                    return jsonify({"message": "patient deja existant", "patient": _patient_payload_from_row(existing)}), 200

                conn.exec_driver_sql(
                    """
                    INSERT INTO patient (nom, prenom, telephone)
                    VALUES (%s, %s, %s)
                    """,
                    (nom, prenom, telephone),
                )

                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE telephone = %s
                    LIMIT 1
                    """,
                    (telephone,),
                ).mappings().first()

            return jsonify({"message": "patient cree avec succes", "patient": _patient_payload_from_row(patient_row)}), 201

        if statut == 2:
            with db.engine.begin() as conn:
                existing = conn.exec_driver_sql(
                    """
                    SELECT id_personnel, nom, prenom, specialite, disponibilite
                    FROM personnel_de_sante
                    WHERE nom = %s AND prenom = %s AND specialite = %s
                    LIMIT 1
                    """,
                    (nom, prenom, specialite),
                ).mappings().first()

                if existing:
                    return jsonify({
                        "message": "personnel medical deja existant",
                        "user": {
                            "id": int(existing["id_personnel"]),
                            "nom": existing["nom"],
                            "prenom": existing["prenom"],
                            "specialite": existing["specialite"],
                            "disponibilite": bool(existing["disponibilite"]),
                        }
                    }), 200

                conn.exec_driver_sql(
                    """
                    INSERT INTO personnel_de_sante (nom, prenom, specialite, disponibilite)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nom, prenom, specialite, 1),
                )

                staff_row = conn.exec_driver_sql(
                    """
                    SELECT id_personnel, nom, prenom, specialite, disponibilite
                    FROM personnel_de_sante
                    WHERE nom = %s AND prenom = %s AND specialite = %s
                    LIMIT 1
                    """,
                    (nom, prenom, specialite),
                ).mappings().first()

            return jsonify({
                "message": "personnel medical cree avec succes",
                "user": {
                    "id": int(staff_row["id_personnel"]),
                    "nom": staff_row["nom"],
                    "prenom": staff_row["prenom"],
                    "specialite": staff_row["specialite"],
                    "disponibilite": bool(staff_row["disponibilite"]),
                }
            }), 201

        return jsonify({"error": "statut invalide (doit etre 1 pour patient ou 2 pour personnel medical)"}), 400

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json() or {}

        user_type = (data.get("userType") or "patient").strip().lower()

        if user_type == "medical_staff":
            staff_row = None
            with db.engine.connect() as conn:
                candidates = conn.exec_driver_sql(
                    """
                    SELECT id_personnel, nom, prenom, specialite, disponibilite
                    FROM personnel_de_sante
                    ORDER BY id_personnel ASC
                    """
                ).mappings().all()

                if candidates:
                    staff_row = candidates[0]

            if not staff_row:
                return jsonify({"error": "personnel medical introuvable"}), 404

            token = create_jwt_token(int(staff_row["id_personnel"]), "medical_staff")
            return jsonify({
                "message": "Connexion reussie",
                "token": token,
                "user": {
                    "id": int(staff_row["id_personnel"]),
                    "nom": staff_row["nom"],
                    "prenom": staff_row["prenom"],
                    "role": "medical_staff",
                    "userType": "medical_staff",
                    "specialite": staff_row["specialite"],
                    "disponibilite": bool(staff_row["disponibilite"]),
                    "staffCategory": "medical_staff"
                }
            }), 200

        # Mode patient: telephone only
        telephone = (data.get("telephone") or "").strip()

        if not telephone:
            return jsonify({"error": "telephone obligatoire"}), 400

        _ensure_patient_table_columns()

        patient_row = None
        with db.engine.connect() as conn:
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE telephone = %s
                LIMIT 1
                """,
                (telephone,),
            ).mappings().first()

        if not patient_row:
            return jsonify({"error": "identifiants patient incorrects"}), 401

        token = create_jwt_token(int(patient_row["id_patient"]), "patient")
        return jsonify({
            "message": "Connexion reussie",
            "token": token,
            "user": {
                "id": int(patient_row["id_patient"]),
                "nom": patient_row["nom"],
                "prenom": patient_row["prenom"],
                "telephone": patient_row["telephone"],
                "role": "patient",
                "userType": "patient"
            }
        }), 200

    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/users", methods=["GET"])
def get_users():
    """Legacy endpoint - user table has been deprecated. Returns combined patients and staff."""
    try:
        _ensure_patient_table_columns()
        patients = []
        staff = []
        
        with db.engine.connect() as conn:
            patient_rows = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                ORDER BY nom ASC, prenom ASC
                """
            ).mappings().all()
            
            for row in patient_rows:
                patients.append({
                    "id": row["id_patient"],
                    "nom": row["nom"],
                    "prenom": row["prenom"],
                    "email": row["email"],
                    "telephone": row["telephone"],
                    "role": "patient",
                    "statut": 1
                })
            
            staff_rows = conn.exec_driver_sql(
                """
                SELECT id_personnel, nom, prenom, specialite, disponibilite
                FROM personnel_de_sante
                ORDER BY nom ASC, prenom ASC
                """
            ).mappings().all()
            
            for row in staff_rows:
                staff.append({
                    "id": row["id_personnel"],
                    "nom": row["nom"],
                    "prenom": row["prenom"],
                    "specialite": row["specialite"],
                    "region": row.get("region"),
                    "role": "medical_staff",
                    "statut": 2,
                    "disponibilite": bool(row["disponibilite"]),
                })
        
        return jsonify(patients + staff), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500

@app.route("/medical-staff", methods=["GET"])
@debug_route
def get_medical_staff():
    try:
        specialite = request.args.get('specialite', '')
        region = request.args.get('region', '')

        query = """
            SELECT id_personnel, nom, prenom, specialite, region, disponibilite
            FROM personnel_de_sante
            WHERE 1=1
        """
        params = []
        if specialite:
            query += " AND LOWER(specialite) LIKE LOWER(%s)"
            params.append(f"%{specialite}%")
        if region:
            query += " AND LOWER(region) LIKE LOWER(%s)"
            params.append(f"%{region}%")
            
        query += " ORDER BY nom ASC, prenom ASC"

        with db.engine.connect() as conn:
            personnel_rows = conn.exec_driver_sql(query, tuple(params)).mappings().all()
            
        payload = []
        for staff in personnel_rows:
            row = dict(staff)
            payload.append(
                {
                    "id": row["id_personnel"],
                    "id_personnel": row["id_personnel"],
                    "nom": row["nom"],
                    "prenom": row["prenom"],
                    "specialite": row["specialite"],
                    "region": row.get("region"),
                    "disponibilite": bool(row["disponibilite"]),
                }
            )
        return jsonify(payload), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500

@app.route("/medical-staff/patient-by-cin", methods=["GET"])
@debug_route
def get_medical_staff_patient_by_cin():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        cin = (request.args.get("cin") or "").strip()

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400
        if not cin:
            return jsonify({"error": "cin est obligatoire"}), 400

        personnel = _get_personnel_row(id_personnel)
        if not personnel:
            return jsonify({"error": f"Personnel #{id_personnel} introuvable"}), 404

        _ensure_patient_table_columns()

        with db.engine.connect() as conn:
            patient = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE LOWER(TRIM(cin)) = %s
                LIMIT 1
                """,
                (cin.lower(),),
            ).mappings().first()

        if not patient:
            return jsonify({"found": False, "cin": cin}), 404

        return jsonify(
            {
                "found": True,
                "patient": _patient_payload_from_row(patient),
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-save", methods=["POST"])
@debug_route
def save_medical_staff_patient():
    try:
        data = request.get_json() or {}
        id_personnel = data.get("idPersonnel")
        patient_payload = data.get("patient") or {}

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        personnel = _get_personnel_row(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404

        nom = str(patient_payload.get("nom") or "").strip()
        prenom = str(patient_payload.get("prenom") or "").strip()
        cin = str(patient_payload.get("cin") or "").strip()
        telephone = str(patient_payload.get("telephone") or "").strip() or None
        email = str(patient_payload.get("email") or "").strip().lower()

        if not nom or not prenom:
            return jsonify({"error": "nom et prenom sont obligatoires"}), 400

        _ensure_patient_table_columns()

        with db.engine.begin() as conn:
            existing_patient = None
            if cin:
                existing_patient = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE telephone = %s
                    LIMIT 1
                    """,
                    (telephone,),
                ).mappings().first()

            if existing_patient:
                conn.exec_driver_sql(
                    """
                    UPDATE patient
                    SET nom = %s,
                        prenom = %s,
                        telephone = %s
                    WHERE id_patient = %s
                    """,
                    (
                        nom,
                        prenom,
                        telephone,
                        int(existing_patient["id_patient"]),
                    ),
                )
                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE id_patient = %s
                    LIMIT 1
                    """,
                    (int(existing_patient["id_patient"]),),
                ).mappings().first()

                return jsonify(
                    {
                        "message": "patient mis a jour avec succes",
                        "created": False,
                        "patient": _patient_payload_from_row(patient_row),
                    }
                ), 200

            insert_result = conn.exec_driver_sql(
                """
                INSERT INTO patient (nom, prenom, telephone)
                VALUES (%s, %s, %s)
                """,
                (nom, prenom, telephone),
            )

            inserted_patient_id = int(insert_result.lastrowid or 0)
            patient_row = None
            if inserted_patient_id:
                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE id_patient = %s
                    LIMIT 1
                    """,
                    (inserted_patient_id,),
                ).mappings().first()

        return jsonify(
            {
                "message": "patient cree avec succes",
                "created": True,
                "patient": _patient_payload_from_row(patient_row),
            }
        ), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/planning", methods=["GET"])
@debug_route
def get_medical_staff_planning():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        selected_date = parse_date(request.args.get("date")) or datetime.utcnow().date()

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        with db.engine.connect() as conn:
            personnel_row = conn.exec_driver_sql(
                """
                SELECT id_personnel, specialite, disponibilite
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (id_personnel,),
            ).mappings().first()

            week_start = selected_date - timedelta(days=selected_date.weekday())
            week_end = week_start + timedelta(days=6)

            rdvs = conn.exec_driver_sql(
                """
                SELECT
                    r.idRDV AS id,
                    r.idPatient,
                    r.idPersonnel,
                    r.dateRDV,
                    r.heureDebut,
                    r.heureFin,
                    r.motifConsultation,
                    p.nom AS patientNom,
                                        p.prenom AS patientPrenom,
                                        ps.nom AS medecinNom,
                                        ps.prenom AS medecinPrenom,
                                        ps.specialite AS specialite
                FROM rdv r
                LEFT JOIN patient p ON p.id_patient = r.idPatient
                                LEFT JOIN personnel_de_sante ps ON ps.id_personnel = r.idPersonnel
                WHERE r.idPersonnel = %s
                  AND r.dateRDV >= %s
                  AND r.dateRDV <= %s
                ORDER BY r.dateRDV ASC, r.heureDebut ASC
                """,
                (id_personnel, week_start, week_end),
            ).mappings().all()

        grouped = {}
        for rdv in rdvs:
            day_key = rdv["dateRDV"].isoformat() if hasattr(rdv["dateRDV"], "isoformat") else str(rdv["dateRDV"])
            grouped.setdefault(day_key, []).append(
                {
                    "id": rdv["id"],
                    "idPatient": rdv["idPatient"],
                    "idPersonnel": rdv["idPersonnel"],
                    "dateRDV": day_key,
                    "heureDebut": _format_sql_time(rdv["heureDebut"]),
                    "heureFin": _format_sql_time(rdv["heureFin"]),
                    "motifConsultation": rdv["motifConsultation"],
                    "statut": "Confirme",
                    "patientNom": rdv["patientNom"] or "",
                    "patientPrenom": rdv["patientPrenom"] or "",
                    "medecinNom": rdv["medecinNom"] or "",
                    "medecinPrenom": rdv["medecinPrenom"] or "",
                    "medecin": f"{(rdv['medecinPrenom'] or '').strip()} {(rdv['medecinNom'] or '').strip()}".strip() or "",
                    "specialite": rdv["specialite"] or "Generaliste",
                }
            )

        week_planning = []
        for offset in range(7):
            current_day = week_start + timedelta(days=offset)
            day_key = current_day.isoformat()
            day_appointments = grouped.get(day_key, [])
            week_planning.append(
                {
                    "date": day_key,
                    "count": len(day_appointments),
                    "appointments": day_appointments,
                }
            )

        today_planning = grouped.get(selected_date.isoformat(), [])

        return jsonify(
            {
                "idPersonnel": id_personnel,
                "date": selected_date.isoformat(),
                "weekStart": week_start.isoformat(),
                "weekEnd": week_end.isoformat(),
                "todayPlanning": today_planning,
                "weekPlanning": week_planning,
                "stats": {
                    "todayCount": len(today_planning),
                    "weekCount": len(rdvs),
                },
            }
        ), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/cancel-all", methods=["POST"])
@debug_route
def cancel_all_medical_staff_day():
    try:
        data = request.get_json() or {}
        id_personnel = data.get("idPersonnel") or request.args.get("idPersonnel", type=int)
        date_value = data.get("date") or request.args.get("date")
        target_date = parse_date(date_value) or datetime.utcnow().date()

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        if not is_medical_staff(int(id_personnel)):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        rdvs = (
            Rdv.query
            .filter(Rdv.idPersonnel == int(id_personnel), Rdv.dateRDV == target_date)
            .all()
        )

        if not rdvs:
            return jsonify({"message": "Aucun rendez-vous a annuler", "count": 0}), 200

        updated = []
        try:
            for r in rdvs:
                old_motif = (r.motifConsultation or "").strip()
                if not old_motif.lower().startswith("annule"):
                    r.motifConsultation = f"Annule - {old_motif or 'consultation'}"
                updated.append(r.idRdv)
            db.session.commit()
            try:
                _notify_patients_of_cancellation(updated, target_date)
            except Exception:
                import traceback
                traceback.print_exc()
        except Exception:
            db.session.rollback()
            raise

        socketio.emit("doctor_planning_cancelled", {"idPersonnel": int(id_personnel), "dateRDV": target_date.isoformat(), "cancelled": updated})

        return jsonify({"message": "RDVs annules pour le personnel", "count": len(updated), "cancelled": updated}), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/recalculate-short-absence", methods=["POST"])
@debug_route
def recalculate_short_absence():
    """Recalculate a doctor's day around a short absence window using OR-Tools."""
    try:
        data = request.get_json(silent=True) or {}
        id_personnel = data.get("idPersonnel") or request.args.get("idPersonnel", type=int)
        date_value = data.get("dateRDV") or data.get("date") or request.args.get("date")
        interval = str(data.get("interval") or "morning").strip().lower()
        absence_hours = _coerce_minutes_value(data.get("absenceHours") or data.get("hours") or 1)

        date_rdv = parse_date(date_value) or datetime.utcnow().date()
        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        try:
            id_personnel = int(id_personnel)
        except (TypeError, ValueError):
            return jsonify({"error": "idPersonnel doit etre un entier"}), 400

        if not is_medical_staff(id_personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        day_start, day_end, plannings, used_default_planning = _get_doctor_planning_window(id_personnel, date_rdv)
        if day_end <= day_start:
            return jsonify({"error": "planning invalide"}), 400

        planning_window = {
            "morning": (day_start, day_start + max(1, (day_end - day_start) // 2)),
            "afternoon": (day_start + max(1, (day_end - day_start) // 2), day_end),
            "full-day": (day_start, day_end),
        }
        if interval not in planning_window:
            return jsonify({"error": "intervalle invalide"}), 400

        interval_start, interval_end = planning_window[interval]
        if interval_end <= interval_start:
            return jsonify({"error": "intervalle invalide"}), 400

        max_absence = interval_end - interval_start
        if absence_hours is None or absence_hours <= 0:
            return jsonify({"error": "absenceHours doit etre positive"}), 400
        absence_duration = int(absence_hours) * 60
        if absence_duration > max_absence:
            return jsonify({"error": f"absenceHours depasse la duree disponible pour {interval}"}), 400

        absence_start = interval_start
        absence_end = absence_start + absence_duration

        existing_rdvs = [_build_rdv_snapshot(rdv) for rdv in _get_doctor_rdvs_for_day(id_personnel, date_rdv)]
        if not existing_rdvs:
            return jsonify({
                "message": "aucun rendez-vous a recalculer",
                "updatedRows": [],
                "updatedSchedule": [],
                "absenceWindow": {
                    "start": _to_hhmmss(absence_start),
                    "end": _to_hhmmss(absence_end),
                    "interval": interval,
                },
                "planningContext": {
                    "hasPlanning": not used_default_planning,
                    "planningSource": "default" if used_default_planning else "planning",
                    "planningWindows": len(plannings),
                },
            }), 200

        result = optimize_day_with_absence(existing_rdvs, day_start, day_end, absence_start, absence_end)
        if result is None:
            return jsonify({"error": "Impossible de recalculer le planning avec cette absence"}), 400

        try:
            updated_rows = _apply_optimized_day_plan(id_personnel, date_rdv, result)
            if updated_rows is None:
                db.session.rollback()
                return jsonify({"error": "Impossible de sauvegarder le planning recalcule"}), 500
            db.session.commit()
            try:
                _notify_patients_of_reschedule(updated_rows, date_rdv)
            except Exception:
                # Notification errors should not block API success; log and continue.
                import traceback
                traceback.print_exc()
        except Exception:
            db.session.rollback()
            raise

        updated_schedule = _get_doctor_rdvs_for_day(id_personnel, date_rdv)
        socketio.emit(
            "doctor_planning_rearranged",
            {
                "idPersonnel": id_personnel,
                "dateRDV": date_rdv.isoformat(),
                "absenceWindow": {
                    "start": _to_hhmmss(absence_start),
                    "end": _to_hhmmss(absence_end),
                    "interval": interval,
                },
                "optimizedPlan": result,
            },
        )

        return jsonify({
            "message": "planning recalcule avec succes",
            "updatedRows": updated_rows,
            "optimizedPlan": result,
            "absenceWindow": {
                "start": _to_hhmmss(absence_start),
                "end": _to_hhmmss(absence_end),
                "interval": interval,
            },
            "planningContext": {
                "hasPlanning": not used_default_planning,
                "planningSource": "default" if used_default_planning else "planning",
                "planningWindows": len(plannings),
            },
            "updatedSchedule": [rdv.to_dict() for rdv in updated_schedule],
        }), 200
    except Exception as exc:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-record", methods=["GET"])
@debug_route
def get_medical_staff_patient_record():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        id_patient = request.args.get("idPatient", type=int)
        current_rdv_id = request.args.get("currentRdvId", type=int)

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        personnel = _get_personnel_row(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404

        _ensure_patient_table_columns()
        with db.engine.connect() as conn:
            patient = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (id_patient,),
            ).mappings().first()

        if not patient:
            return jsonify({"error": "patient introuvable"}), 404

        dossier_row = conn.exec_driver_sql(
            """
            SELECT idfiche, idpatient, idpersonnel, nom, prenom, age, etat_civil
            FROM fiche_patient
            WHERE idpatient = %s
            LIMIT 1
            """,
            (id_patient,),
        ).mappings().first()

        rdvs = (
            Rdv.query
            .filter(
                Rdv.idPatient == id_patient,
                Rdv.idPersonnel == id_personnel,
            )
            .order_by(Rdv.dateRDV.desc(), Rdv.heureDebut.desc())
            .all()
        )

        history = []
        for rdv in rdvs:
            if current_rdv_id and rdv.idRdv == current_rdv_id:
                continue

            history.append(
                {
                    "dateRDV": rdv.dateRDV.isoformat(),
                    "heureDebut": _format_sql_time(rdv.heureDebut),
                    "heureFin": _format_sql_time(rdv.heureFin),
                    "motifConsultation": rdv.motifConsultation,
                    "statut": "Confirme",
                }
            )

        return jsonify(
            {
                "patient": {
                    "id": int(patient["id_patient"]),
                    "nom": patient["nom"],
                    "prenom": patient["prenom"],
                    "telephone": patient["telephone"],
                    "email": patient["email"],
                    "cin": patient["cin"],
                    "statut": 1,
                },
                "dossier": {
                    "idfiche": dossier_row["idfiche"] if dossier_row else None,
                    "idpatient": dossier_row["idpatient"] if dossier_row else None,
                    "idpersonnel": dossier_row["idpersonnel"] if dossier_row else None,
                    "nom": dossier_row["nom"] if dossier_row else None,
                    "prenom": dossier_row["prenom"] if dossier_row else None,
                    "age": dossier_row["age"] if dossier_row and dossier_row.get("age") is not None else None,
                    "etat_civil": dossier_row["etat_civil"] if dossier_row else None,
                },
                "currentDoctorId": int(personnel["id_personnel"]),
                "history": history,
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-full-profile", methods=["GET"])
@debug_route
def get_medical_staff_patient_full_profile():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        id_patient = request.args.get("idPatient", type=int)
        current_rdv_id = request.args.get("currentRdvId", type=int)

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        with db.engine.connect() as conn:
            personnel_row = conn.exec_driver_sql(
                """
                SELECT id_personnel
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (id_personnel,),
            ).mappings().first()

            if not personnel_row:
                return jsonify({"error": "personnel introuvable"}), 404

            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (id_patient,),
            ).mappings().first()

            if not patient_row:
                return jsonify({"error": "patient introuvable"}), 404

            dossier_row = conn.exec_driver_sql(
                """
                SELECT idfiche, idpatient, idpersonnel, nom, prenom, age, etat_civil
                FROM fiche_patient
                WHERE idpatient = %s
                LIMIT 1
                """,
                (id_patient,),
            ).mappings().first()

            rdvs = conn.exec_driver_sql(
                """
                SELECT
                    idRDV AS id,
                    dateRDV,
                    heureDebut,
                    heureFin,
                    motifConsultation
                FROM rdv
                WHERE idPatient = %s
                  AND idPersonnel = %s
                ORDER BY dateRDV DESC, heureDebut DESC
                """,
                (id_patient, id_personnel),
            ).mappings().all()

        history = []
        for rdv in rdvs:
            if current_rdv_id and rdv["id"] == current_rdv_id:
                continue

            history.append(
                {
                    "id": rdv["id"],
                    "dateRDV": rdv["dateRDV"].isoformat() if hasattr(rdv["dateRDV"], "isoformat") else str(rdv["dateRDV"]),
                    "heureDebut": _format_sql_time(rdv["heureDebut"]),
                    "heureFin": _format_sql_time(rdv["heureFin"]),
                    "motifConsultation": rdv["motifConsultation"],
                    "statut": None,
                }
            )

        age = dossier_row["age"] if dossier_row and dossier_row.get("age") is not None else None
        nom_complet = f"{(patient_row['prenom'] or '').strip()} {(patient_row['nom'] or '').strip()}".strip()

        return jsonify(
            {
                "patient": {
                    "id": int(patient_row["id_patient"]),
                    "nom": patient_row["nom"],
                    "prenom": patient_row["prenom"],
                    "nomComplet": nom_complet or f"Patient #{patient_row['id_patient']}",
                    "cin": patient_row["cin"],
                    "sexe": None,
                    "telephone": patient_row["telephone"],
                    "email": patient_row["email"],
                    "statut": 1,
                    "statut_label": "patient",
                    "dateNaissance": None,
                    "age": age,
                    "allergies": [],
                    "maladies": [],
                    "idfiche": dossier_row["idfiche"] if dossier_row else None,
                    "idpatient": dossier_row["idpatient"] if dossier_row else None,
                    "idpersonnel": dossier_row["idpersonnel"] if dossier_row else None,
                    "nomFiche": dossier_row["nom"] if dossier_row else None,
                    "prenomFiche": dossier_row["prenom"] if dossier_row else None,
                    "etat_civil": dossier_row["etat_civil"] if dossier_row else None,
                },
                "currentDoctorId": id_personnel,
                "historyCount": len(history),
                "lastAppointment": history[0] if history else None,
                "appointments": history,
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500

@app.route("/medical-staff/patients", methods=["GET"])
@debug_route
def get_medical_staff_patients():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        with db.engine.connect() as conn:
            personnel_row = conn.exec_driver_sql(
                """
                SELECT id_personnel
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (id_personnel,),
            ).mappings().first()

            if not personnel_row:
                app.logger.warning(f"medical staff not found for id_personnel={id_personnel}")
                return jsonify([]), 200

            rows = conn.exec_driver_sql(
                """
                SELECT
                    p.id_patient AS id,
                    p.nom,
                    p.prenom,
                    p.email,
                    p.telephone,
                    COUNT(r.idRdv) AS rdvCount
                FROM patient p
                LEFT JOIN rdv r
                    ON r.idPatient = p.id_patient
                   AND r.idPersonnel = %s
                GROUP BY p.id_patient, p.nom, p.prenom, p.email, p.telephone
                ORDER BY p.nom ASC, p.prenom ASC
                """,
                (id_personnel,),
            ).mappings().all()

        return jsonify([
            {
                "id": int(row["id"]),
                "nom": row["nom"],
                "prenom": row["prenom"],
                "email": row["email"],
                "telephone": row["telephone"],
                "rdvCount": int(row["rdvCount"] or 0),
            }
            for row in rows
        ]), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/today-access", methods=["GET"])
def get_patient_today_access():
    try:
        patient_id, auth_error = _get_authenticated_patient_id()
        # If authentication failed, allow a public fallback when a patientId is provided
        if auth_error:
            pid_param = request.args.get('patientId') or request.args.get('idPatient')
            if pid_param:
                try:
                    patient_id = int(pid_param)
                    auth_error = None
                except Exception:
                    return auth_error
            else:
                return auth_error

        today = datetime.utcnow().date()
        access_payload = _resolve_patient_doctor_status(patient_id, today)

        if not access_payload:
            return jsonify(
                {
                    "access": False,
                    "message": "Acces autorise uniquement le jour de votre rendez-vous",
                }
            ), 403

        return jsonify(access_payload), 200
    except Exception as exc:
        return jsonify({"access": False, "message": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/rdvs", methods=["GET"])
def get_patient_rdvs():
    """Get all RDVs for the authenticated patient with doctor details and statut."""
    try:
        # Extract patient ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou invalide"}), 401
        
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            patient_id = payload.get("user_id")
            user_role = payload.get("role")
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        
        if user_role != "patient" or not patient_id:
            return jsonify({"error": "Acces refuse - patient seulement"}), 403
        
        _ensure_patient_table_columns()
        
        with db.engine.connect() as conn:
            # Verify patient exists
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS adresse
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()
            
            if not patient_row:
                return jsonify({"error": "Patient non trouve"}), 404
            
            # Get all RDVs for this patient with doctor details
            rdvs = conn.exec_driver_sql(
                """
                SELECT
                    r.idRDV AS id,
                    r.dateRDV,
                    r.heureDebut,
                    r.heureFin,
                    r.motifConsultation,
                    ps.id_personnel,
                    ps.nom AS medecin_nom,
                    ps.prenom AS medecin_prenom,
                    ps.specialite
                FROM rdv r
                LEFT JOIN personnel_de_sante ps ON r.idPersonnel = ps.id_personnel
                WHERE r.idPatient = %s
                ORDER BY r.dateRDV DESC, r.heureDebut DESC
                """,
                (patient_id,),
            ).mappings().all()
        
        result = []
        for rdv in rdvs:
            medecin_nom = f"{(rdv.get('medecin_prenom') or '').strip()} {(rdv.get('medecin_nom') or '').strip()}".strip()
            heure_debut = _normalize_sql_time(rdv["heureDebut"])
            heure_fin = _normalize_sql_time(rdv["heureFin"])
            result.append({
                "id": int(rdv["id"]),
                "idRdv": int(rdv["id"]),
                "idRDV": int(rdv["id"]),
                "idPatient": int(patient_id),
                "idPersonnel": int(rdv["id_personnel"]),
                "dateRDV": rdv["dateRDV"].isoformat() if rdv["dateRDV"] else None,
                "heureDebut": heure_debut.strftime("%H:%M:%S") if heure_debut else None,
                "heureFin": heure_fin.strftime("%H:%M:%S") if heure_fin else None,
                "motifConsultation": rdv["motifConsultation"] or "",
                "statut": "Confirme",
                "medecinNom": (rdv.get('medecin_nom') or None),
                "medecinPrenom": (rdv.get('medecin_prenom') or None),
                "medecin": medecin_nom or "Non assigne",
                "specialite": rdv["specialite"] or "Generaliste"
            })
        
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/dossier-medical", methods=["GET"])
def get_patient_dossier_medical():
    """Get patient's medical record (read-only)."""
    try:
        # Extract patient ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou invalide"}), 401
        
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            patient_id = payload.get("user_id")
            user_role = payload.get("role")
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        
        if user_role != "patient" or not patient_id:
            return jsonify({"error": "Acces refuse - patient seulement"}), 403
        
        _ensure_patient_table_columns()
        
        with db.engine.connect() as conn:
            # Get patient info
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()
            
            if not patient_row:
                return jsonify({"error": "Patient non trouve"}), 404
            
            # Get medical record
            dossier_row = conn.exec_driver_sql(
                """
                SELECT
                    idfiche,
                    idpatient,
                    idpersonnel,
                    nom,
                    prenom,
                    age,
                    etat_civil
                FROM fiche_patient
                WHERE idpatient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()
        
        age = dossier_row["age"] if dossier_row and dossier_row.get("age") is not None else None
        
        return jsonify({
            "patient": {
                "id": int(patient_row["id_patient"]),
                "nom": patient_row["nom"],
                "prenom": patient_row["prenom"],
                "email": patient_row["email"],
                "telephone": patient_row["telephone"],
                "cin": patient_row["cin"],
            },
            "dossier": {
                "idfiche": dossier_row["idfiche"] if dossier_row else None,
                "idpatient": dossier_row["idpatient"] if dossier_row else None,
                "idpersonnel": dossier_row["idpersonnel"] if dossier_row else None,
                "nom": dossier_row["nom"] if dossier_row else None,
                "prenom": dossier_row["prenom"] if dossier_row else None,
                "age": age,
                "etat_civil": dossier_row["etat_civil"] if dossier_row else None,
                "sexe": None,
                "date_naissance": None,
                "historique": "",
                "allergies": [],
                "traitements": [],
            }
        }), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/dashboard", methods=["GET"])
def get_patient_dashboard():
    """Aggregate patient dashboard data (profile, medical record, and appointment history)."""
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou invalide"}), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            patient_id = payload.get("user_id")
            user_role = payload.get("role")
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401

        if user_role != "patient" or not patient_id:
            return jsonify({"error": "Acces refuse - patient seulement"}), 403

        _ensure_patient_table_columns()

        with db.engine.connect() as conn:
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()

            if not patient_row:
                return jsonify({"error": "Patient non trouve"}), 404

            dossier_row = conn.exec_driver_sql(
                """
                SELECT idfiche, idpatient, idpersonnel, nom, prenom, age, etat_civil
                FROM fiche_patient
                WHERE idpatient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()

            rdv_rows = conn.exec_driver_sql(
                """
                SELECT
                    r.idRDV AS id,
                    r.dateRDV,
                    r.heureDebut,
                    r.heureFin,
                    r.motifConsultation,
                    ps.nom AS medecin_nom,
                    ps.prenom AS medecin_prenom,
                    ps.specialite
                FROM rdv r
                LEFT JOIN personnel_de_sante ps ON r.idPersonnel = ps.id_personnel
                WHERE r.idPatient = %s
                ORDER BY r.dateRDV DESC, r.heureDebut DESC
                """,
                (patient_id,),
            ).mappings().all()

        appointments = []
        for row in rdv_rows:
            medecin_prenom = (row.get("medecin_prenom") or "").strip()
            medecin_nom = (row.get("medecin_nom") or "").strip()
            medecin_full = f"{medecin_prenom} {medecin_nom}".strip()
            appointments.append(
                {
                    "id": int(row["id"]),
                    "dateRDV": row["dateRDV"].isoformat() if row["dateRDV"] else None,
                    "heureDebut": _format_sql_time(row["heureDebut"]),
                    "heureFin": _format_sql_time(row["heureFin"]),
                    "motifConsultation": row["motifConsultation"] or "",
                    "statut": "Confirme",
                    "medecin": medecin_full or "Medecin non renseigne",
                    "medecinNom": medecin_nom or None,
                    "medecinPrenom": medecin_prenom or None,
                    "specialite": row["specialite"] or "Generaliste",
                }
            )

        age = dossier_row["age"] if dossier_row and dossier_row.get("age") is not None else None

        nom_complet = f"{(patient_row['prenom'] or '').strip()} {(patient_row['nom'] or '').strip()}".strip()

        return jsonify(
            {
                "patient": {
                    "id": int(patient_row["id_patient"]),
                    "nom": patient_row["nom"],
                    "prenom": patient_row["prenom"],
                    "nomComplet": nom_complet,
                    "email": patient_row["email"],
                    "telephone": patient_row["telephone"],
                    "cin": patient_row["cin"],
                    "adresse": None,
                },
                "dossierMedical": {
                    "idfiche": dossier_row["idfiche"] if dossier_row else None,
                    "idpatient": dossier_row["idpatient"] if dossier_row else None,
                    "idpersonnel": dossier_row["idpersonnel"] if dossier_row else None,
                    "nom": dossier_row["nom"] if dossier_row else None,
                    "prenom": dossier_row["prenom"] if dossier_row else None,
                    "age": age,
                    "etat_civil": dossier_row["etat_civil"] if dossier_row else None,
                    "sexe": None,
                    "dateNaissance": None,
                    "historique": "",
                    "allergies": [],
                    "maladies": [],
                },
                "historyCount": len(appointments),
                "appointments": appointments,
                "lastAppointment": appointments[0] if appointments else None,
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500
@app.route("/patient/profile", methods=["GET"])
def get_patient_profile():
    """Get complete patient profile (read-only) with medical data and recent appointments."""
    try:
        # Extract patient ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou invalide"}), 401
        
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            patient_id = payload.get("user_id")
            user_role = payload.get("role")
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        
        if user_role != "patient" or not patient_id:
            return jsonify({"error": "Acces refuse - patient seulement"}), 403
        
        _ensure_patient_table_columns()
        
        with db.engine.connect() as conn:
            # Get patient info
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()
            
            if not patient_row:
                return jsonify({"error": "Patient non trouve"}), 404
            
            # Get medical record
            dossier_row = conn.exec_driver_sql(
                """
                SELECT
                    idfiche,
                    idpatient,
                    idpersonnel,
                    nom,
                    prenom,
                    age,
                    etat_civil
                FROM fiche_patient
                WHERE idpatient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()
            
            # Get recent appointments (last 10)
            appointments_rows = conn.exec_driver_sql(
                """
                SELECT
                    r.idRDV AS id,
                    r.dateRDV,
                    r.heureDebut,
                    r.heureFin,
                    r.motifConsultation,
                    ps.nom AS medecin_nom,
                    ps.prenom AS medecin_prenom,
                    ps.specialite
                FROM rdv r
                LEFT JOIN personnel_de_sante ps ON r.idPersonnel = ps.id_personnel
                WHERE r.idPatient = %s
                ORDER BY r.dateRDV DESC, r.heureDebut DESC
                LIMIT 10
                """,
                (patient_id,),
            ).mappings().all()
        
        # Process appointments
        appointments = []
        for row in appointments_rows:
            medecin_prenom = (row.get("medecin_prenom") or "").strip()
            medecin_nom = (row.get("medecin_nom") or "").strip()
            medecin_full = f"{medecin_prenom} {medecin_nom}".strip()
            appointments.append({
                "id": int(row["id"]),
                "dateRDV": row["dateRDV"].isoformat() if row["dateRDV"] else None,
                "heureDebut": _format_sql_time(row["heureDebut"]),
                "heureFin": _format_sql_time(row["heureFin"]),
                "motifConsultation": row["motifConsultation"] or "consultation",
                "statut": row["statut"] or "Confirme",
                "medecinNom": medecin_nom,
                "medecinPrenom": medecin_prenom,
                "medecin": medecin_full,
                "specialite": (row.get("specialite") or "Généraliste")
            })
        
        age = dossier_row["age"] if dossier_row and dossier_row.get("age") is not None else None
        
        return jsonify({
            "patient": {
                "id": int(patient_row["id_patient"]),
                "nom": patient_row["nom"],
                "prenom": patient_row["prenom"],
                "email": patient_row["email"] or "",
                "telephone": patient_row["telephone"] or "",
                "cin": patient_row["cin"] or "",
                "adresse": patient_row["adresse"] or "",
                "dateNaissance": None,
                "age": age,
                "sexe": None,
            },
            "dossier": {
                "idfiche": dossier_row["idfiche"] if dossier_row else None,
                "idpatient": dossier_row["idpatient"] if dossier_row else None,
                "idpersonnel": dossier_row["idpersonnel"] if dossier_row else None,
                "nom": dossier_row["nom"] if dossier_row else None,
                "prenom": dossier_row["prenom"] if dossier_row else None,
                "age": age,
                "etat_civil": dossier_row["etat_civil"] if dossier_row else None,
            },
            "allergies": [],
            "maladies": [],
            "historiqueMedical": "",
            "appointments": appointments,
        }), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


def _get_authenticated_patient_id():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Token manquant ou invalide"}), 401)

    token = auth_header[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Token invalide"}), 401)

    patient_id = payload.get("user_id")
    user_role = payload.get("role")
    if user_role != "patient" or not patient_id:
        return None, (jsonify({"error": "Acces refuse - patient seulement"}), 403)

    return int(patient_id), None


@app.route("/patient/profile/address", methods=["PUT"])
def update_patient_profile_address():
    try:
        patient_id, auth_error = _get_authenticated_patient_id()
        if auth_error:
            return auth_error

        data = request.get_json() or {}
        address = str(data.get("adresse") or data.get("address") or "").strip()
        if not address:
            return jsonify({"error": "adresse est obligatoire"}), 400

        _ensure_patient_table_columns()
        with db.engine.begin() as conn:
            result = conn.exec_driver_sql(
                "UPDATE patient SET adresse = %s WHERE id_patient = %s",
                (address, patient_id),
            )

        return jsonify({"message": "adresse patient mise a jour", "adresse": address}), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/travel-notices", methods=["GET"])
def get_patient_travel_notices():
    try:
        patient_id, auth_error = _get_authenticated_patient_id()
        if auth_error:
            return auth_error

        clinic_address = (request.args.get("clinicAddress") or DEFAULT_CLINIC_ADDRESS).strip()
        _ensure_patient_table_columns()

        with db.engine.connect() as conn:
            patient_row = conn.exec_driver_sql(
                """
                SELECT id_patient, adresse, nom, prenom
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (patient_id,),
            ).mappings().first()

            if not patient_row:
                return jsonify({"error": "Patient non trouve"}), 404

            appointments_rows = conn.exec_driver_sql(
                """
                SELECT idRDV AS id, dateRDV, heureDebut, heureFin, motifConsultation
                FROM rdv
                WHERE idPatient = %s
                  AND dateRDV >= CURDATE()
                ORDER BY dateRDV ASC, heureDebut ASC
                LIMIT 12
                """,
                (patient_id,),
            ).mappings().all()

        patient_address = (patient_row.get("adresse") or "").strip()
        notices = []
        for appointment in appointments_rows:
            appointment_date = appointment.get("dateRDV")
            appointment_time = appointment.get("heureDebut")
            appointment_dt = None
            if appointment_date and appointment_time:
                appointment_dt = datetime.combine(appointment_date, appointment_time)

            if not patient_address:
                notices.append({
                    "rdvId": int(appointment["id"]),
                    "appointmentDate": appointment_date.isoformat() if appointment_date else None,
                    "appointmentTime": appointment_time.strftime("%H:%M:%S") if appointment_time else None,
                    "notice": {
                        "status": "error",
                        "message": "Renseignez votre adresse pour calculer le trajet.",
                        "recommendation": "Renseignez votre adresse pour calculer le trajet.",
                    },
                })
                continue

            cached_notice = _get_cached_travel_notice(patient_id, int(appointment["id"]))
            notice = cached_notice or get_travel_notice(patient_address, clinic_address, appointment_dt)
            if notice.get("status") == "ok" and cached_notice is None:
                _store_travel_notice_cache(patient_id, int(appointment["id"]), notice)
            notices.append({
                "rdvId": int(appointment["id"]),
                "appointmentDate": appointment_date.isoformat() if appointment_date else None,
                "appointmentTime": appointment_time.strftime("%H:%M:%S") if appointment_time else None,
                "notice": notice,
            })

        return jsonify({
            "patientId": patient_id,
            "patientAddress": patient_address,
            "clinicAddress": clinic_address,
            "notices": notices,
        }), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/patient/travel-notice", methods=["POST"])
def get_patient_travel_notice():
    try:
        patient_id, auth_error = _get_authenticated_patient_id()
        if auth_error:
            return auth_error

        data = request.get_json() or {}
        clinic_address = (data.get("clinicAddress") or DEFAULT_CLINIC_ADDRESS).strip()
        appointment_time = data.get("appointmentTime") or data.get("appointmentDateTime")
        patient_address = str(data.get("patientAddress") or "").strip()

        if not patient_address:
            _ensure_patient_table_columns()
            with db.engine.connect() as conn:
                patient_row = conn.exec_driver_sql(
                    "SELECT adresse FROM patient WHERE id_patient = %s LIMIT 1",
                    (patient_id,),
                ).mappings().first()
            patient_address = (patient_row.get("adresse") or "").strip() if patient_row else ""

        if not patient_address:
            return jsonify({"error": "adresse patient manquante"}), 400

        if not appointment_time:
            return jsonify({"error": "appointmentTime est obligatoire"}), 400

        notice = get_travel_notice(patient_address, clinic_address, appointment_time)
        notice["patientId"] = patient_id
        return jsonify(notice), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


def _travel_notice_cache_key(patient_id: int, rdv_id: int) -> tuple[int, int]:
    return int(patient_id), int(rdv_id)


def _get_cached_travel_notice(patient_id: int, rdv_id: int):
    cache_entry = TRAVEL_NOTICE_CACHE.get(_travel_notice_cache_key(patient_id, rdv_id))
    if not cache_entry:
        return None

    cached_at = cache_entry.get("cachedAt")
    if isinstance(cached_at, datetime):
        if (datetime.utcnow() - cached_at).total_seconds() > TRAVEL_NOTICE_CACHE_TTL_SECONDS:
            TRAVEL_NOTICE_CACHE.pop(_travel_notice_cache_key(patient_id, rdv_id), None)
            return None

    return cache_entry.get("notice")


def _store_travel_notice_cache(patient_id: int, rdv_id: int, notice: dict):
    TRAVEL_NOTICE_CACHE[_travel_notice_cache_key(patient_id, rdv_id)] = {
        "cachedAt": datetime.utcnow(),
        "notice": notice,
    }


def _refresh_travel_notice_cache():
    try:
        # The patient table no longer stores addresses, so live travel notices are disabled.
        TRAVEL_NOTICE_CACHE.clear()
    except Exception:
        app.logger.exception("Erreur lors du rafraichissement des notices de trajet")


def _travel_notice_worker():
    while True:
        _refresh_travel_notice_cache()
        threading.Event().wait(TRAVEL_NOTICE_REFRESH_SECONDS)


def start_travel_notice_worker():
    global TRAVEL_NOTICE_WORKER_STARTED
    if TRAVEL_NOTICE_WORKER_STARTED:
        return

    TRAVEL_NOTICE_WORKER_STARTED = True
    worker = threading.Thread(target=_travel_notice_worker, daemon=True)
    worker.start()

@app.route("/medical-staff/patient-full-profile/update", methods=["PUT"])
def update_medical_staff_patient_full_profile():
    try:
        data = request.get_json() or {}
        id_personnel = data.get("idPersonnel")
        id_patient = data.get("idPatient")
        payload = data.get("patient") or {}

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        personnel = _get_personnel_row(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel medical introuvable"}), 404

        _ensure_patient_table_columns()

        with db.engine.begin() as conn:
            patient = conn.exec_driver_sql(
                """
                SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                FROM patient
                WHERE id_patient = %s
                LIMIT 1
                """,
                (int(id_patient),),
            ).mappings().first()

            if not patient:
                return jsonify({"error": "patient introuvable"}), 404

            if payload.get("nom") is not None:
                conn.exec_driver_sql(
                    "UPDATE patient SET nom = %s WHERE id_patient = %s",
                    (str(payload.get("nom") or "").strip() or patient["nom"], int(id_patient)),
                )
            if payload.get("prenom") is not None:
                conn.exec_driver_sql(
                    "UPDATE patient SET prenom = %s WHERE id_patient = %s",
                    (str(payload.get("prenom") or "").strip() or patient["prenom"], int(id_patient)),
                )
            if payload.get("email") is not None:
                conn.exec_driver_sql(
                    "UPDATE patient SET email = %s WHERE id_patient = %s",
                    (str(payload.get("email") or "").strip() or None, int(id_patient)),
                )
            if payload.get("telephone") is not None:
                conn.exec_driver_sql(
                    "UPDATE patient SET telephone = %s WHERE id_patient = %s",
                    (str(payload.get("telephone") or "").strip() or None, int(id_patient)),
                )
            if payload.get("cin") is not None:
                cin_value = str(payload.get("cin") or "").strip() or None
                conn.exec_driver_sql(
                    "UPDATE patient SET cin = %s, password = %s WHERE id_patient = %s",
                    (cin_value, cin_value or "", int(id_patient)),
                )

        return jsonify({"message": "profil patient mis a jour"}), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/suggest-available-slots", methods=["POST"])
def suggest_available_slots():
    try:
        data = request.get_json() or {}

        id_personnel = data.get("idPersonnel")
        date_rdv = parse_date(data.get("dateRDV"))
        slot_duration = data.get("slotDuration", 30)
        is_urgent = bool(data.get("isUrgent", False))
        proposal_index = data.get("proposalIndex", 0)

        if not id_personnel or not date_rdv:
            return jsonify({"error": "idPersonnel et dateRDV sont obligatoires"}), 400

        try:
            id_personnel = int(id_personnel)
        except (TypeError, ValueError):
            return jsonify({"error": "idPersonnel doit etre un entier"}), 400

        try:
            slot_duration = int(slot_duration)
        except (TypeError, ValueError):
            return jsonify({"error": "slotDuration doit etre un entier"}), 400

        try:
            proposal_index = int(proposal_index)
        except (TypeError, ValueError):
            return jsonify({"error": "proposalIndex doit etre un entier"}), 400

        if slot_duration <= 0:
            return jsonify({"error": "slotDuration doit etre superieur a 0"}), 400

        if proposal_index < 0:
            proposal_index = 0

        with db.engine.connect() as conn:
            personnel_row = conn.exec_driver_sql(
                """
                SELECT id_personnel, specialite, disponibilite
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (id_personnel,),
            ).mappings().first()

        if not personnel_row:
            return jsonify({"error": "personnel introuvable"}), 404

        plannings = (
            Planning.query
            .filter_by(idPersonnel=id_personnel, date=date_rdv)
            .order_by(Planning.heure_debut.asc())
            .all()
        )

        with db.engine.connect() as conn:
            appointment_rows = conn.exec_driver_sql(
                """
                SELECT idRDV, heureDebut, heureFin
                FROM rdv
                WHERE idPersonnel = %s AND dateRDV = %s
                ORDER BY heureDebut ASC
                """,
                (id_personnel, date_rdv),
            ).mappings().all()

        appointments = [
            {
                "idRdv": row["idRDV"],
                "heureDebut": row["heureDebut"],
                "heureFin": row["heureFin"],
            }
            for row in appointment_rows
        ]

        if is_urgent:
            existing = [
                {
                    "id": r["idRdv"],
                    "start": _to_minutes(r["heureDebut"]),
                    "duration": _to_minutes(r["heureFin"]) - _to_minutes(r["heureDebut"]),
                }
                for r in appointments
                if r["heureDebut"] is not None and r["heureFin"] is not None
            ]

            if plannings:
                window_start = min(_to_minutes(plan.heure_debut) for plan in plannings)
                window_end = max(_to_minutes(plan.heure_fin) for plan in plannings)
            else:
                window_start = 9 * 60
                window_end = 17 * 60

            result = schedule_with_emergency(
                existing_rdvs=existing,
                duration=slot_duration,
                start_window=window_start,
                end_window=window_end,
            )

            if not result:
                return jsonify({"error": "Impossible d'inserer l'urgence"}), 200

            return jsonify(
                {
                    "type": "urgent_optimized",
                    "dateRDV": date_rdv.isoformat(),
                    "idPersonnel": id_personnel,
                    "isUrgent": True,
                    "slotDuration": slot_duration,
                    "urgentSlot": {
                        "heureDebut": _to_hhmmss(result["urgent_start"]),
                        "heureFin": _to_hhmmss(result["urgent_end"]),
                    },
                    "rescheduledAppointments": result["updated"],
                    "optimizedPlan": result.get("optimized_plan", []),
                }
            ), 200

        booked_ranges = [(_to_minutes(r["heureDebut"]), _to_minutes(r["heureFin"])) for r in appointments]

        planning_ranges = []
        for plan in plannings:
            planning_ranges.append((_to_minutes(plan.heure_debut), _to_minutes(plan.heure_fin)))

        # Fallback: if no planning is defined for the selected date, suggest slots on a default day window.
        used_default_planning = False
        if not planning_ranges:
            planning_ranges = [(9 * 60, 17 * 60)]
            used_default_planning = True

        # Build basic suggested slots using current bookings (no shifting)
        suggested_slots = []
        for start_min, end_min in planning_ranges:
            if end_min <= start_min:
                continue

            cursor = start_min
            while cursor + slot_duration <= end_min:
                slot_start = cursor
                slot_end = cursor + slot_duration

                overlaps = any(slot_start < booked_end and slot_end > booked_start for booked_start, booked_end in booked_ranges)
                if not overlaps:
                    suggested_slots.append(
                        {
                            "heureDebut": _to_hhmmss(slot_start),
                            "heureFin": _to_hhmmss(slot_end),
                        }
                    )

                cursor += slot_duration

        # Extra: attempt an OR-Tools based compaction of the day's appointments to remove small gaps.
        # If successful, also compute suggested slots against the optimized (shifted) schedule so
        # the frontend can offer an "optimized" view (appointments shifted to fill gaps).
        optimized_suggested_slots = None
        optimized_appointments = None
        try:
            # Build normalized patients list: id and duration
            normalized = []
            for r in appointments:
                if r.get("heureDebut") is None or r.get("heureFin") is None:
                    continue
                dur = _to_minutes(r["heureFin"]) - _to_minutes(r["heureDebut"])
                if dur <= 0:
                    continue
                normalized.append({"id": r.get("idRdv"), "duration": dur})

            # Use the overall planning window, but keep the real booked span when it extends
            # outside of the configured planning window (common with legacy data).
            earliest_booked_start = min((start for start, _ in booked_ranges), default=None)
            latest_booked_end = max((end for _, end in booked_ranges), default=None)
            overall_start = min(start for start, _ in planning_ranges)
            overall_end = max(end for _, end in planning_ranges)
            if earliest_booked_start is not None:
                overall_start = min(overall_start, earliest_booked_start)
            if latest_booked_end is not None:
                overall_end = max(overall_end, latest_booked_end)

            if normalized:
                compact = optimize_full_day(normalized, overall_start, overall_end)
                if compact:
                    optimized_appointments = compact
                    # Build booked ranges from optimized plan
                    opt_booked = []
                    for ap in compact:
                        tstart = parse_time(ap.get("heureDebut"))
                        tend = parse_time(ap.get("heureFin"))
                        if tstart is None or tend is None:
                            continue
                        opt_booked.append(( _to_minutes(tstart), _to_minutes(tend) ))

                    # Compute suggested slots against optimized bookings
                    opt_slots = []
                    for start_min, end_min in planning_ranges:
                        if end_min <= start_min:
                            continue
                        cursor = start_min
                        while cursor + slot_duration <= end_min:
                            slot_start = cursor
                            slot_end = cursor + slot_duration
                            overlaps_opt = any(slot_start < booked_end and slot_end > booked_start for booked_start, booked_end in opt_booked)
                            if not overlaps_opt:
                                opt_slots.append({"heureDebut": _to_hhmmss(slot_start), "heureFin": _to_hhmmss(slot_end)})
                            cursor += slot_duration
                    optimized_suggested_slots = opt_slots
        except Exception:
            optimized_suggested_slots = None
            optimized_appointments = None

        candidate_slots = optimized_suggested_slots or suggested_slots
        if candidate_slots:
            selected_slot = candidate_slots[proposal_index % len(candidate_slots)]
            suggested_slots = [selected_slot]
            optimized_suggested_slots = [selected_slot] if optimized_suggested_slots else None

        week_start = date_rdv - timedelta(days=date_rdv.weekday())
        week_end = week_start + timedelta(days=6)

        week_count = (
            Rdv.query
            .filter(
                Rdv.idPersonnel == id_personnel,
                Rdv.dateRDV >= week_start,
                Rdv.dateRDV <= week_end,
            )
            .count()
        )

        response = {
            "dateRDV": date_rdv.isoformat(),
            "idPersonnel": id_personnel,
            "isUrgent": is_urgent,
            "slotDuration": slot_duration,
            "proposalIndex": proposal_index,
            "planningContext": {
                "weekStart": week_start.isoformat(),
                "weekEnd": week_end.isoformat(),
                "todayAppointments": len(appointments),
                "weekAppointments": week_count,
                "hasPlanning": not used_default_planning,
                "planningWindows": len(planning_ranges),
                "planningSource": "default" if used_default_planning else "planning",
            },
            "suggestedSlots": suggested_slots,
            "optimizedSuggestedSlots": optimized_suggested_slots,
            "optimizedPlan": optimized_appointments,
        }

        return jsonify(response), 200

    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/add_rdv", methods=["POST"])
def add_rdv():
    try:
        data = request.get_json() or {}
        
        print(f"\n>>> /add_rdv - Received request")
        print(f"    Raw data: {data}")

        id_patient = data.get("idPatient")
        patient_nom = (data.get("nom") or data.get("patientNom") or "").strip()
        patient_prenom = (data.get("prenom") or data.get("patientPrenom") or "").strip()
        id_personnel = data.get("idPersonnel")
        date_rdv = parse_date(data.get("dateRDV"))
        heure_debut = parse_time(data.get("heureDebut"))
        heure_fin = parse_time(data.get("heureFin"))
        statut = data.get("statut") or data.get("motifConsultation")
        is_urgent = bool(data.get("isUrgent", False))
        urgent_duration = _coerce_minutes_value(
            data.get("slotDuration") or data.get("duration") or data.get("duree_creneau")
        )
        
        print(f"    Parsed: patient={patient_nom} {patient_prenom}, personnel={id_personnel}, date={date_rdv}, time={heure_debut}-{heure_fin}, statut={statut}")

        statut = _normalize_status(statut)

        if not all([id_personnel, date_rdv]):
            msg = f"Missing required fields: personnel={id_personnel}, date={date_rdv}"
            print(f"    ERROR: {msg}")
            return jsonify({"error": "idPersonnel et dateRDV sont obligatoires"}), 400

        if not is_urgent and not all([heure_debut, heure_fin]):
            msg = f"Missing required fields: start={heure_debut}, end={heure_fin}"
            print(f"    ERROR: {msg}")
            return jsonify({"error": "idPersonnel, dateRDV, heureDebut et heureFin sont obligatoires"}), 400

        if is_urgent:
            statut = RDV_URGENT_STATUT
            if urgent_duration is None:
                if heure_debut and heure_fin:
                    urgent_duration = _to_minutes(heure_fin) - _to_minutes(heure_debut)
                else:
                    urgent_duration = 30
            if urgent_duration <= 0:
                return jsonify({"error": "slotDuration ou la duree du créneau urgent doit être superieure a 0"}), 400
        else:
            statut = "Confirme"

        _ensure_patient_table_columns()
        
        patient_row = None
        with db.engine.begin() as conn:
            if id_patient and int(id_patient) > 0:
                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE id_patient = %s
                    LIMIT 1
                    """,
                    (int(id_patient),),
                ).mappings().first()
                if patient_row:
                    print(f"    Using existing patient ID {id_patient}")
                else:
                    print(f"    ERROR: Patient ID {id_patient} not found in patient table")
                    return jsonify({"error": "patient introuvable"}), 404
            elif patient_nom and patient_prenom:
                # Generate unique email if not provided or if it already exists
                email = (data.get("email") or "").strip()
                existing = conn.exec_driver_sql(
                    """
                    SELECT id_patient FROM patient
                    WHERE LOWER(email) = LOWER(%s)
                    LIMIT 1
                    """,
                    (email or _generate_unique_patient_email(),),
                ).mappings().first()
                
                if not email or existing:
                    # Email is missing or already exists - generate a unique one
                    email = _generate_unique_patient_email()
                    print(f"    Generated unique email: {email}")
                
                conn.exec_driver_sql(
                    """
                    INSERT INTO patient (nom, prenom, telephone)
                    VALUES (%s, %s, %s)
                    """,
                    (patient_nom, patient_prenom, data.get("telephone") or ""),
                )
                
                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    WHERE telephone = %s
                    LIMIT 1
                    """,
                    (data.get("telephone") or "",),
                ).mappings().first()
                
                if patient_row:
                    id_patient = patient_row["id_patient"]
                    print(f"    Created new patient ID {id_patient}: {patient_nom} {patient_prenom}")
            else:
                # Get first patient as fallback
                fallback_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient, nom, prenom, telephone, NULL AS email, NULL AS cin, NULL AS password
                    FROM patient
                    ORDER BY id_patient ASC
                    LIMIT 1
                    """
                ).mappings().first()
                
                if not fallback_row:
                    print(f"    ERROR: No fallback patient available")
                    return jsonify({"error": "aucun patient disponible pour creer un RDV public"}), 400
                
                patient_row = fallback_row
                id_patient = fallback_row["id_patient"]
                print(f"    Using fallback patient ID {id_patient}")

        if not patient_row:
            print(f"    ERROR: Patient not found")
            return jsonify({"error": "patient introuvable"}), 404

        if not is_medical_staff(id_personnel):
            print(f"    ERROR: Personnel is not medical staff")
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        if not is_urgent:
            requested_slot_duration = _coerce_minutes_value(
                data.get("slotDuration") or data.get("duration") or data.get("duree_creneau")
            )
            if requested_slot_duration is None and heure_debut and heure_fin:
                requested_slot_duration = _to_minutes(heure_fin) - _to_minutes(heure_debut)

            if requested_slot_duration is None or requested_slot_duration <= 0:
                return jsonify({"error": "duree de creneau invalide"}), 400

            slot_payload = _build_available_slots_for_doctor(int(id_personnel), date_rdv, requested_slot_duration)
            allowed_slots = slot_payload.get("optimizedSuggestedSlots") or slot_payload.get("suggestedSlots") or []
            allowed_pairs = {
                (
                    _format_sql_time(parse_time(slot.get("heureDebut")), "%H:%M:%S"),
                    _format_sql_time(parse_time(slot.get("heureFin")), "%H:%M:%S"),
                )
                for slot in allowed_slots
                if slot.get("heureDebut") and slot.get("heureFin")
            }

            requested_pair = (
                _format_sql_time(heure_debut, "%H:%M:%S"),
                _format_sql_time(heure_fin, "%H:%M:%S"),
            )

            if requested_pair not in allowed_pairs:
                print(f"    ERROR: Requested slot {requested_pair} is not among OR-Tools proposed slots")
                return jsonify({
                    "error": "Veuillez choisir un creneau propose par OR-Tools",
                    "allowedSlots": allowed_slots,
                }), 400

        if is_urgent:
            print("    URGENT: insertion urgente demandee", flush=True)
            # Use a single atomic operation to compute and persist the urgent insertion
            def perform_urgent_planning_and_persist(id_personnel, date_rdv, id_patient, payload, urgent_duration):
                window_start, window_end, plannings, used_default_planning = _get_doctor_planning_window(id_personnel, date_rdv)
                existing_rdvs = [_build_rdv_snapshot(rdv) for rdv in _get_doctor_rdvs_for_day(id_personnel, date_rdv)]

                now_reference = None
                try:
                    if date_rdv == datetime.now().date():
                        now_reference = datetime.now().hour * 60 + datetime.now().minute
                except Exception:
                    now_reference = None

                immediate_result = _find_immediate_urgent_slot(
                    existing_rdvs=existing_rdvs,
                    duration=urgent_duration,
                    start_window=window_start,
                    end_window=window_end,
                    reference_minute=now_reference,
                )

                if immediate_result:
                    print(
                        f"    URGENT: créneau immédiat trouvé { _to_hhmmss(immediate_result['urgent_start']) } -> { _to_hhmmss(immediate_result['urgent_end']) }",
                        flush=True,
                    )
                    try:
                        try:
                            db.session.rollback()
                        except Exception:
                            pass
                        with db.session.begin():
                            urgent_rdv = Rdv(
                                idPatient=id_patient,
                                idPersonnel=id_personnel,
                                dateRDV=date_rdv,
                                heureDebut=parse_time(_to_hhmmss(immediate_result["urgent_start"])),
                                heureFin=parse_time(_to_hhmmss(immediate_result["urgent_end"])),
                                motifConsultation=payload.get("motifConsultation") or "Urgence patient",
                            )
                            db.session.add(urgent_rdv)
                            db.session.flush()

                            updated_schedule = _get_doctor_rdvs_for_day(id_personnel, date_rdv)

                        print("    URGENT: aucun déplacement effectué", flush=True)
                        return {
                            "urgent_rdv": urgent_rdv.to_dict(),
                            "urgent_start": immediate_result["urgent_start"],
                            "urgent_end": immediate_result["urgent_end"],
                            "rescheduledAppointments": [],
                            "optimizedPlan": immediate_result.get("optimized_plan", []),
                            "updatedSchedule": [rdv.to_dict() for rdv in updated_schedule],
                            "planningContext": {
                                "hasPlanning": not used_default_planning,
                                "planningSource": "default" if used_default_planning else "planning",
                                "planningWindows": len(plannings),
                                "mode": "immediate",
                            },
                        }, (window_start, window_end, plannings, used_default_planning)
                    except Exception as exc:
                        print(f"    ERROR persisting immediate urgent planning: {exc}", flush=True)
                        try:
                            db.session.rollback()
                        except Exception:
                            pass
                        return None, (None, None, plannings, used_default_planning)

                if not existing_rdvs and not plannings and urgent_duration > (window_end - window_start):
                    return None, (None, None, plannings, used_default_planning)

                result = schedule_with_emergency(
                    existing_rdvs=existing_rdvs,
                    duration=urgent_duration,
                    start_window=window_start,
                    end_window=window_end,
                )

                if not result:
                    return None, (None, None, plannings, used_default_planning)

                print(f"    URGENT: recalcul planning OR-Tools, deplacements={len(result.get('updated', []))}", flush=True)

                # Persist all changes in a single DB transaction. If anything fails, rollback.
                try:
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    with db.session.begin():
                        persisted = _apply_rescheduled_appointments(id_personnel, date_rdv, result)
                        if not persisted:
                            # Let the transaction rollback by raising
                            raise RuntimeError("failed to persist rescheduled appointments")

                        urgent_rdv = Rdv(
                            idPatient=id_patient,
                            idPersonnel=id_personnel,
                            dateRDV=date_rdv,
                            heureDebut=persisted["urgent_start"],
                            heureFin=persisted["urgent_end"],
                            motifConsultation=payload.get("motifConsultation") or "Urgence patient",
                        )
                        db.session.add(urgent_rdv)
                        db.session.flush()

                        # Capture the updated schedule after commit
                        updated_schedule = _get_doctor_rdvs_for_day(id_personnel, date_rdv)

                    # After successful commit, notify and return persistent results
                    return {
                        "urgent_rdv": urgent_rdv.to_dict(),
                        "urgent_start": persisted["urgent_start"],
                        "urgent_end": persisted["urgent_end"],
                        "rescheduledAppointments": result.get("updated", []),
                        "optimizedPlan": result.get("optimized_plan", []) if isinstance(result, dict) else result.get("optimized_plan", []),
                        "updatedSchedule": [rdv.to_dict() for rdv in updated_schedule],
                        "planningContext": {
                            "hasPlanning": not used_default_planning,
                            "planningSource": "default" if used_default_planning else "planning",
                            "planningWindows": len(plannings),
                            "mode": "recalculated",
                        },
                    }, (window_start, window_end, plannings, used_default_planning)
                except Exception as exc:
                    print(f"    ERROR persisting urgent planning: {exc}", flush=True)
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    return None, (None, None, plannings, used_default_planning)

            persisted_result, planning_meta = perform_urgent_planning_and_persist(int(id_personnel), date_rdv, int(id_patient), data, urgent_duration)

            if not persisted_result:
                return jsonify({"error": "Impossible d'inserer l'urgence ou de sauvegarder le reordonnancement"}), 500

            # Emit socket event after successful commit
            socketio.emit(
                "doctor_planning_rearranged",
                {
                    "idPersonnel": int(id_personnel),
                    "dateRDV": date_rdv.isoformat(),
                    "urgentRdv": persisted_result["urgent_rdv"],
                    "rescheduledAppointments": persisted_result["rescheduledAppointments"],
                },
            )

            return jsonify({
                "message": "rdv urgent cree avec succes",
                "type": "urgent_optimized",
                "rdv": persisted_result["urgent_rdv"],
                "urgentSlot": {
                    "heureDebut": _format_time_for_client(persisted_result["urgent_start"]),
                    "heureFin": _format_time_for_client(persisted_result["urgent_end"]),
                },
                "rescheduledAppointments": persisted_result["rescheduledAppointments"],
                "optimizedPlan": persisted_result.get("optimizedPlan", []),
                "planningContext": persisted_result.get("planningContext", {}),
                "updatedSchedule": persisted_result.get("updatedSchedule", []),
                "isUrgent": True,
            }), 201

        # Check for appointment conflicts for normal consultations/controls.
        has_conflict, conflicting_rdv = check_appointment_conflict(id_personnel, date_rdv, heure_debut, heure_fin)
        if has_conflict and conflicting_rdv:
            conflict_info = {
                "heureDebut": _format_sql_time(conflicting_rdv.heureDebut),
                "heureFin": _format_sql_time(conflicting_rdv.heureFin),
                "patientNom": patient_row["nom"] if patient_row else "Inconnu",
                "patientPrenom": patient_row["prenom"] if patient_row else "",
            }
            print(f"    ERROR: Conflict detected with RDV {conflicting_rdv.idRdv}")
            return jsonify({
                "error": "Le creneau demande est deja occupe par un autre rendez-vous",
                "conflictingAppointment": conflict_info
            }), 409

        rdv = Rdv(
            idPatient=id_patient,
            idPersonnel=id_personnel,
            dateRDV=date_rdv,
            heureDebut=heure_debut,
            heureFin=heure_fin,
            motifConsultation=data.get("motifConsultation", ""),
        )
        
        print(f"    Creating RDV...")

        db.session.add(rdv)
        db.session.commit()
        
        print(f"    SUCCESS: RDV #{rdv.idRdv} created")
        print(f"<<< /add_rdv - Response: 201\n")

        return jsonify({"message": "rdv cree avec succes", "rdv": rdv.to_dict()}), 201

    except Exception as exc:
        db.session.rollback()
        print(f"    EXCEPTION: {str(exc)}")
        import traceback
        traceback.print_exc()
        print(f"<<< /add_rdv - Response: 500\n")
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/rdvs", methods=["GET"])
def get_rdvs():
    try:
        rdvs = Rdv.query.all()
        return jsonify([r.to_dict() for r in rdvs]), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/get_rdvs", methods=["GET"])
def get_rdvs_legacy():
    return get_rdvs()


@app.route("/update_rdv/<int:rdv_id>", methods=["PUT"])
def update_rdv(rdv_id):
    try:
        data = request.get_json() or {}
        rdv = Rdv.query.get(rdv_id)

        if not rdv:
            return jsonify({"error": "rdv introuvable"}), 404

        _ensure_patient_table_columns()
        
        if "idPatient" in data:
            with db.engine.connect() as conn:
                patient_row = conn.exec_driver_sql(
                    """
                    SELECT id_patient FROM patient WHERE id_patient = %s LIMIT 1
                    """,
                    (int(data["idPatient"]),),
                ).mappings().first()
            
            if not patient_row:
                return jsonify({"error": "patient introuvable"}), 404
            rdv.idPatient = data["idPatient"]

        if "idPersonnel" in data:
            if not is_medical_staff(int(data["idPersonnel"])):
                return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400
            rdv.idPersonnel = data["idPersonnel"]

        if "dateRDV" in data:
            parsed_date = parse_date(data.get("dateRDV"))
            if not parsed_date:
                return jsonify({"error": "dateRDV invalide (format YYYY-MM-DD)"}), 400
            rdv.dateRDV = parsed_date

        # Parse new times but defer assigning to rdv until validation
        parsed_start = None
        parsed_end = None
        if "heureDebut" in data:
            parsed_start = parse_time(data.get("heureDebut"))
            if not parsed_start:
                return jsonify({"error": "heureDebut invalide (format HH:MM ou HH:MM:SS)"}), 400

        if "heureFin" in data:
            parsed_end = parse_time(data.get("heureFin"))
            if not parsed_end:
                return jsonify({"error": "heureFin invalide (format HH:MM ou HH:MM:SS)"}), 400

        # If times or date/personnel are being changed, validate the requested slot
        try:
            effective_personnel = int(data.get("idPersonnel", rdv.idPersonnel))
        except Exception:
            effective_personnel = rdv.idPersonnel

        effective_date = None
        if "dateRDV" in data:
            effective_date = parsed_date
        else:
            effective_date = rdv.dateRDV

        # Determine effective start/end times for validation (use parsed if provided, else existing)
        effective_start = parsed_start if parsed_start is not None else rdv.heureDebut
        effective_end = parsed_end if parsed_end is not None else rdv.heureFin

        if effective_start and effective_end:
            requested_slot_duration = _coerce_minutes_value(data.get("slotDuration") or data.get("duration") or data.get("duree_creneau"))
            if requested_slot_duration is None:
                requested_slot_duration = _to_minutes(effective_end) - _to_minutes(effective_start)

            if requested_slot_duration is None or requested_slot_duration <= 0:
                return jsonify({"error": "duree de creneau invalide"}), 400

            slot_payload = _build_available_slots_for_doctor(int(effective_personnel), effective_date, requested_slot_duration)
            allowed_slots = slot_payload.get("optimizedSuggestedSlots") or slot_payload.get("suggestedSlots") or []
            allowed_pairs = {
                (
                    _format_sql_time(parse_time(slot.get("heureDebut")), "%H:%M:%S"),
                    _format_sql_time(parse_time(slot.get("heureFin")), "%H:%M:%S"),
                )
                for slot in allowed_slots
                if slot.get("heureDebut") and slot.get("heureFin")
            }

            requested_pair = (
                _format_sql_time(effective_start, "%H:%M:%S"),
                _format_sql_time(effective_end, "%H:%M:%S"),
            )

            if requested_pair not in allowed_pairs:
                print(f"    ERROR: Requested update slot {requested_pair} is not among OR-Tools proposed slots")
                return jsonify({
                    "error": "Veuillez choisir un creneau propose par OR-Tools",
                    "allowedSlots": allowed_slots,
                }), 400

        # Assign parsed values now that validation passed
        if parsed_start is not None:
            rdv.heureDebut = parsed_start
        if parsed_end is not None:
            rdv.heureFin = parsed_end

        if "motifConsultation" in data:
            rdv.motifConsultation = data["motifConsultation"]

        db.session.commit()
        return jsonify({"message": "rdv mis a jour avec succes", "rdv": rdv.to_dict()}), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/delete_rdv/<int:rdv_id>", methods=["DELETE"])
def delete_rdv(rdv_id):
    try:
        rdv = Rdv.query.get(rdv_id)
        if not rdv:
            return jsonify({"error": "rdv introuvable"}), 404

        db.session.delete(rdv)
        db.session.commit()

        return jsonify({"message": "rdv supprime avec succes"}), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/add_planning", methods=["POST"])
def add_planning():
    try:
        data = request.get_json() or {}

        plan_date = parse_date(data.get("date"))
        heure_debut = parse_time(data.get("heure_debut"))
        heure_fin = parse_time(data.get("heure_fin"))
        duree_creneau = data.get("duree_creneau")
        id_personnel = data.get("idPersonnel")

        if not all([plan_date, heure_debut, heure_fin, duree_creneau, id_personnel]):
            return jsonify({"error": "date, heure_debut, heure_fin, duree_creneau et idPersonnel sont obligatoires"}), 400

        try:
            duree_creneau = int(duree_creneau)
        except (TypeError, ValueError):
            return jsonify({"error": "duree_creneau doit etre un entier"}), 400

        if duree_creneau <= 0:
            return jsonify({"error": "duree_creneau doit etre superieure a 0"}), 400

        with db.engine.connect() as conn:
            personnel_row = conn.exec_driver_sql(
                """
                SELECT id_personnel, specialite, disponibilite
                FROM personnel_de_sante
                WHERE id_personnel = %s
                LIMIT 1
                """,
                (id_personnel,),
            ).mappings().first()

        if not personnel_row:
            return jsonify({"error": "personnel introuvable"}), 404

        planning = Planning(
            date=plan_date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            duree_creneau=duree_creneau,
            idPersonnel=id_personnel,
        )

        db.session.add(planning)
        db.session.commit()

        return jsonify({"message": "planning cree avec succes", "planning": planning.to_dict()}), 201

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/planning", methods=["GET"])
def get_planning():
    try:
        planning = Planning.query.all()
        return jsonify([p.to_dict() for p in planning]), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        data = request.get_json(silent=True) or {}
        patients = data.get("patients", [])
        doctor_schedule = data.get("doctor_schedule", {})

        app.logger.info(
            "Optimize request received: patients=%s doctor_schedule=%s",
            len(patients) if isinstance(patients, list) else "invalid",
            doctor_schedule,
        )

        optimized_schedule = optimize_schedule(patients, doctor_schedule)
        if optimized_schedule is None:
            app.logger.warning("No feasible optimization solution found")
            return jsonify({
                "status": "error",
                "message": "impossible de trouver un planning compatible avec les contraintes",
                "data": [],
            }), 400

        app.logger.info("Optimization success: appointments=%s", len(optimized_schedule))
        return jsonify({"status": "success", "data": optimized_schedule}), 200
    except Exception as exc:
        app.logger.exception("Server error during optimization")
        return jsonify({
            "status": "error",
            "message": f"erreur serveur: {str(exc)}",
            "data": [],
        }), 500


@app.route("/optimize-day", methods=["POST"])
def optimize_day():
    try:
        data = request.get_json(silent=True) or {}
        patients = data.get("patients", [])
        if not isinstance(patients, list):
            return jsonify({"error": "patients must be a list"}), 400
        result = optimize_full_day(
            patients=patients,
            start_window=9 * 60,
            end_window=17 * 60,
        )
        if result is None:
            return jsonify({"error": "impossible d'optimiser la journee"}), 400
        return jsonify({"status": "success", "data": result}), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500

def optimize():
    try:
        data = request.get_json(silent=True) or {}
        patients = data.get("patients", [])
        doctor_schedule = data.get("doctor_schedule", {})

        app.logger.info(
            "Optimize request received: patients=%s doctor_schedule=%s",
            len(patients) if isinstance(patients, list) else "invalid",
            doctor_schedule,
        )

        optimized_schedule = optimize_schedule(patients, doctor_schedule)
        if optimized_schedule is None:
            app.logger.warning("No feasible optimization solution found")
            return jsonify({
                "status": "error",
                "message": "impossible de trouver un planning compatible avec les contraintes",
                "data": [],
            }), 400

        app.logger.info("Optimization success: appointments=%s", len(optimized_schedule))
        return jsonify({"status": "success", "data": optimized_schedule}), 200
    except Exception as exc:
        app.logger.exception("Server error during optimization")
        return jsonify({
            "status": "error",
            "message": f"erreur serveur: {str(exc)}",
            "data": [],
        }), 500


@app.route("/", methods=["GET"])
def health_check():
    db_ready = refresh_db_status()
    status_code = 200 if db_ready else 503
    return jsonify({
        "message": "API Flask operationnelle",
        "database": "connected" if db_ready else "unavailable",
    }), status_code


def initialize_database():
    global DB_READY
    try:
        with app.app_context():
            db.create_all()
            migrate_mysql_schema()
        DB_READY = True
    except Exception as exc:
        DB_READY = False
        app.logger.warning("Database unavailable at startup: %s", str(exc))


initialize_database()


@socketio.on("connect")
def handle_socket_connect():
    print(f"[SocketIO] client connected: {request.sid}", flush=True)


@socketio.on("disconnect")
def handle_socket_disconnect():
    print(f"[SocketIO] client disconnected: {request.sid}", flush=True)


@socketio.on("message")
def handle_message(data):
    print(f"[SocketIO] message recu: {data}", flush=True)
    return {"status": "ok", "echo": data}


@socketio.on("request_cabinet_status")
def handle_cabinet_status_request():
    """Handle patient request for real-time cabinet status"""
    print(f"[SocketIO] Cabinet status requested by {request.sid}", flush=True)
    
    try:
        # Get current time to check if cabinet is open
        from datetime import datetime, time as time_type
        current_time = datetime.now().time()
        
        # Cabinet hours: typically 8:00 - 18:00
        cabinet_open_time = time_type(8, 0)
        cabinet_close_time = time_type(18, 0)
        is_open = cabinet_open_time <= current_time <= cabinet_close_time
        
        # Get count of current appointments today
        today = datetime.now().date()
        current_rdvs = db.session.query(Rdv).filter(Rdv.dateRDV == today).all()
        
        total_patients = len(current_rdvs)
        
        # Check if any doctor is available today
        doctors_today = db.session.query(Planning).filter(
            Planning.date == today
        ).all()
        doctor_available = len(doctors_today) > 0
        
        # Estimate wait time based on number of patients
        # Assuming each appointment takes ~20 minutes
        wait_time = max(0, (total_patients - 1) * 20)
        
        cabinet_status = {
            "isOpen": is_open,
            "doctorAvailable": doctor_available,
            "waitTime": wait_time,
            "totalPatients": total_patients,
            "message": "Bienvenue! Le cabinet est actuellement ouvert." if is_open else "Le cabinet est fermé. Nous vous accueillerons demain."
        }
        
        socketio.emit('cabinet_status_update', cabinet_status, to=request.sid)
        print(f"[SocketIO] Cabinet status sent: {cabinet_status}", flush=True)
        
    except Exception as e:
        print(f"[SocketIO] Error getting cabinet status: {str(e)}", flush=True)
        socketio.emit('cabinet_status_update', {
            "isOpen": False,
            "doctorAvailable": False,
            "waitTime": 0,
            "totalPatients": 0,
            "message": "Erreur lors de la récupération du statut du cabinet."
        }, to=request.sid)


@app.route("/medical-staff/optimize-planning", methods=["POST"])
def optimize_and_persist_planning():
    """Optimize and persist a doctor's planning for one date.

    Payload:
      - idPersonnel: required
      - dateRDV: required
    """
    try:
        data = request.get_json(silent=True) or {}
        id_personnel = data.get("idPersonnel")
        date_rdv = parse_date(data.get("dateRDV"))

        if not id_personnel or not date_rdv:
            return jsonify({"error": "idPersonnel et dateRDV sont obligatoires"}), 400

        try:
            id_personnel = int(id_personnel)
        except (TypeError, ValueError):
            return jsonify({"error": "idPersonnel doit etre un entier"}), 400

        if not is_medical_staff(id_personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        window_start, window_end, plannings, used_default_planning = _get_doctor_planning_window(id_personnel, date_rdv)
        existing_rdvs = _get_doctor_rdvs_for_day(id_personnel, date_rdv)

        if not existing_rdvs:
            return jsonify({"message": "aucun rendez-vous a optimiser", "updatedRows": [], "planningContext": {"hasPlanning": not used_default_planning, "planningSource": "default" if used_default_planning else "planning"}}), 200

        booked_ranges = [(_to_minutes(rdv.heureDebut), _to_minutes(rdv.heureFin)) for rdv in existing_rdvs if rdv.heureDebut and rdv.heureFin]
        normalized = []
        for rdv in existing_rdvs:
            if rdv.heureDebut is None or rdv.heureFin is None:
                continue
            duration = _to_minutes(rdv.heureFin) - _to_minutes(rdv.heureDebut)
            if duration <= 0:
                continue
            normalized.append({"id": rdv.idRdv, "duration": duration})

        if not normalized:
            return jsonify({"error": "impossible de calculer un planning optimisable"}), 400

        earliest_booked_start = min((start for start, _ in booked_ranges), default=window_start)
        latest_booked_end = max((end for _, end in booked_ranges), default=window_end)
        overall_start = min(window_start, earliest_booked_start)
        overall_end = max(window_end, latest_booked_end)

        optimized_plan = optimize_full_day(normalized, overall_start, overall_end)
        if optimized_plan is None:
            return jsonify({"error": "impossible d'optimiser le planning"}), 400

        with db.session.begin():
            updated_rows = _apply_optimized_day_plan(id_personnel, date_rdv, optimized_plan)
            if updated_rows is None:
                db.session.rollback()
                return jsonify({"error": "impossible de sauvegarder le planning optimise"}), 500

        updated_schedule = _get_doctor_rdvs_for_day(id_personnel, date_rdv)
        socketio.emit(
            "doctor_planning_rearranged",
            {
                "idPersonnel": id_personnel,
                "dateRDV": date_rdv.isoformat(),
                "optimizedPlan": optimized_plan,
            },
        )

        return jsonify(
            {
                "message": "planning optimise avec succes",
                "updatedRows": updated_rows,
                "optimizedPlan": optimized_plan,
                "planningContext": {
                    "hasPlanning": not used_default_planning,
                    "planningSource": "default" if used_default_planning else "planning",
                    "planningWindows": len(plannings),
                },
                "updatedSchedule": [rdv.to_dict() for rdv in updated_schedule],
            }
        ), 200
    except Exception as exc:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


if __name__ == "__main__":
    start_travel_notice_worker()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)












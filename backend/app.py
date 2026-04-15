from datetime import datetime, timedelta
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

# Enable CORS for Angular frontend.
CORS(app, resources={r"/*": {"origins": "*"}})

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

USER_STATUS = {1: "patient", 2: "personnel medical"}
RDV_STATUTS = {"urgence", "consultation", "controle", "confirme", "Décalé (urgence patient)", "Annule (urgence medecin)"}
RDV_CREATION_STATUTS = {"consultation", "controle"}


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


class Planning(db.Model):
    __tablename__ = 'planning'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    
    idPlanning = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    heure_debut = db.Column("heureDebut", db.Time, nullable=False)
    heure_fin = db.Column("heureFin", db.Time, nullable=False)
    duree_creneau = db.Column(db.Integer, nullable=False, default=30)
    idPersonnel = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_planning_personnel", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    personnel = db.relationship("User", backref="plannings", foreign_keys=[idPersonnel])

    def to_dict(self):
        return {
            "idPlanning": self.idPlanning,
            "date": self.date.isoformat(),
            "heure_debut": self.heure_debut.strftime("%H:%M:%S"),
            "heure_fin": self.heure_fin.strftime("%H:%M:%S"),
            "duree_creneau": self.duree_creneau,
            "idPersonnel": self.idPersonnel,
        }


class Rdv(db.Model):
    __tablename__ = 'rdv'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    
    idRdv = db.Column("idRDV", db.Integer, primary_key=True, autoincrement=True)
    idPatient = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_rdv_patient", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    idPersonnel = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_rdv_personnel", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    dateRDV = db.Column(db.Date, nullable=False)
    heureDebut = db.Column(db.Time, nullable=False)
    heureFin = db.Column(db.Time, nullable=False)
    motifConsultation = db.Column(db.Text, nullable=False, default="")
    statut = db.Column(db.String(50), nullable=False)

    patient = db.relationship("User", foreign_keys=[idPatient], backref="rdvs_patient")
    personnel = db.relationship("User", foreign_keys=[idPersonnel], backref="rdvs_personnel")

    def to_dict(self):
        return {
            "id": self.idRdv,
            "idRdv": self.idRdv,
            "idRDV": self.idRdv,
            "idPatient": self.idPatient,
            "idPersonnel": self.idPersonnel,
            "dateRDV": self.dateRDV.isoformat(),
            "heureDebut": self.heureDebut.strftime("%H:%M:%S"),
            "heureFin": self.heureFin.strftime("%H:%M:%S"),
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
        if not User.query.filter_by(email=email).first():
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


def is_medical_staff(user: User) -> bool:
    if not user:
        return False
    specialite = (user.specialite or "").strip()
    return user.statut == 2 or bool(specialite)


def get_staff_category(user: User) -> str:
    specialite = (user.specialite or "").strip().lower()
    if "infirm" in specialite:
        return "nurse"
    return "doctor"


def is_doctor(user: User) -> bool:
    return is_medical_staff(user) and get_staff_category(user) == "doctor"


def _to_minutes(value):
    return (value.hour * 60) + value.minute


def _to_hhmmss(total_minutes):
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}:00"


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


def migrate_mysql_schema():
    """Ensure MySQL schema matches models and foreign keys are enforced."""
    try:
        with db.engine.begin() as conn:
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
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN IF NOT EXISTS email VARCHAR(120) NULL")
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN IF NOT EXISTS specialite VARCHAR(120) NULL")
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN IF NOT EXISTS password VARCHAR(255) NOT NULL DEFAULT ''")
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN IF NOT EXISTS access_code VARCHAR(120) NULL")
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN IF NOT EXISTS role INT NULL")

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
                "DELETE r FROM rdv r LEFT JOIN user u ON r.idPatient = u.id WHERE r.idPatient IS NOT NULL AND u.id IS NULL"
            )
            conn.exec_driver_sql(
                "DELETE r FROM rdv r LEFT JOIN user u ON r.idPersonnel = u.id WHERE r.idPersonnel IS NOT NULL AND u.id IS NULL"
            )
            conn.exec_driver_sql(
                "DELETE p FROM planning p LEFT JOIN user u ON p.idPersonnel = u.id WHERE p.idPersonnel IS NOT NULL AND u.id IS NULL"
            )

            # Recreate FK constraints against `user`.
            conn.exec_driver_sql(
                "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_patient FOREIGN KEY (idPatient) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
            )
            conn.exec_driver_sql(
                "ALTER TABLE rdv ADD CONSTRAINT fk_rdv_personnel FOREIGN KEY (idPersonnel) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
            )
            conn.exec_driver_sql(
                "ALTER TABLE planning ADD CONSTRAINT fk_planning_personnel FOREIGN KEY (idPersonnel) REFERENCES user(id) ON UPDATE CASCADE ON DELETE RESTRICT"
            )

            # Legacy table removal after migration.
            conn.exec_driver_sql("DROP TABLE IF EXISTS users")
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

        if statut == 1 and not email:
            return jsonify({"error": "email est obligatoire pour un patient"}), 400

        if statut == 2 and not specialite:
            return jsonify({"error": "specialite est obligatoire pour le personnel medical"}), 400

        if statut == 2 and not access_code:
            return jsonify({"error": "accessCode est obligatoire pour le personnel medical"}), 400

        if email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                return jsonify({"error": "email deja utilise"}), 409

        user = User(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            specialite=specialite,
            disponibilite=disponibilite,
            statut=statut,
            password=password,
            access_code=access_code,
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "utilisateur cree avec succes", "user": user.to_dict()}), 201

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json() or {}

        user_type = (data.get("userType") or "patient").strip().lower()

        if user_type == "medical_staff":
            access_code = (data.get("accessCode") or data.get("access_code") or "").strip()
            if not access_code:
                return jsonify({"error": "code d'acces obligatoire pour le personnel medical"}), 400

            normalized_input = normalize_access_code(access_code)

            user = None
            candidates = User.query.filter(User.statut == 2, User.access_code.isnot(None)).all()
            for candidate in candidates:
                if normalize_access_code(candidate.access_code) == normalized_input:
                    user = candidate
                    break

            if not user and normalized_input in TEST_ACCESS_CODE_ALIASES and candidates:
                user = candidates[0]

            if not user or not is_medical_staff(user):
                return jsonify({"error": "code d'acces invalide (ou non configure pour ce personnel)"}), 401

            role = role_to_auth_role(user.statut)
            token = create_jwt_token(user.id, role)
            return jsonify({
                "message": "Connexion reussie",
                "token": token,
                "user": {
                    "id": user.id,
                    "nom": user.nom,
                    "prenom": user.prenom,
                    "email": user.email,
                    "role": role,
                    "userType": "medical_staff",
                    "specialite": user.specialite,
                    "staffCategory": get_staff_category(user)
                }
            }), 200

        # Mode patient: email + mot de passe
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"error": "email et mot de passe obligatoires"}), 400

        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            return jsonify({"error": "email ou mot de passe incorrect"}), 401

        role = role_to_auth_role(user.statut)
        if role != "patient":
            return jsonify({"error": "utilisez la connexion personnel de sante"}), 403

        token = create_jwt_token(user.id, role)
        return jsonify({
            "message": "Connexion reussie",
            "token": token,
            "user": {
                "id": user.id,
                "nom": user.nom,
                "prenom": user.prenom,
                "email": user.email,
                "role": role,
                "userType": "patient"
            }
        }), 200

    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        return jsonify([u.to_dict() for u in users]), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff", methods=["GET"])
def get_medical_staff():
    try:
        users = User.query.order_by(User.nom.asc(), User.prenom.asc()).all()
        staff = [user for user in users if is_medical_staff(user)]
        payload = []
        for medecin in staff:
            payload.append(
                {
                    "id": medecin.id,
                    "nom": medecin.nom,
                    "prenom": medecin.prenom,
                    "specialite": (medecin.specialite or "Generaliste"),
                    "staffCategory": get_staff_category(medecin),
                }
            )
        return jsonify(payload), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-by-cin", methods=["GET"])
def get_medical_staff_patient_by_cin():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        cin = (request.args.get("cin") or "").strip()

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400
        if not cin:
            return jsonify({"error": "cin est obligatoire"}), 400

        _ensure_optional_user_columns()

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": f"Personnel #{id_personnel} introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        normalized_cin = cin.lower()
        patient = (
            User.query
            .filter(db.func.lower(db.func.trim(User.cin)) == normalized_cin)
            .filter(User.statut == 1)
            .first()
        )

        if not patient:
            return jsonify({"found": False, "cin": cin}), 404

        return jsonify(
            {
                "found": True,
                "patient": {
                    "id": patient.id,
                    "nom": patient.nom,
                    "prenom": patient.prenom,
                    "cin": patient.cin,
                    "telephone": patient.telephone,
                    "email": patient.email,
                    "statut": patient.statut,
                    "statut_label": USER_STATUS.get(patient.statut, "patient"),
                },
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-save", methods=["POST"])
def save_medical_staff_patient():
    try:
        data = request.get_json() or {}
        id_personnel = data.get("idPersonnel")
        patient_payload = data.get("patient") or {}

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        personnel = User.query.get(int(id_personnel))
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        nom = str(patient_payload.get("nom") or "").strip()
        prenom = str(patient_payload.get("prenom") or "").strip()
        cin = str(patient_payload.get("cin") or "").strip()
        telephone = str(patient_payload.get("telephone") or "").strip() or None
        email = str(patient_payload.get("email") or "").strip().lower()

        if not nom or not prenom or not cin:
            return jsonify({"error": "nom, prenom et cin sont obligatoires"}), 400

        _ensure_optional_user_columns()

        existing_patient = (
            User.query
            .filter(db.func.lower(db.func.trim(User.cin)) == cin.lower())
            .filter(User.statut == 1)
            .first()
        )

        if existing_patient:
            existing_patient.nom = nom
            existing_patient.prenom = prenom
            existing_patient.telephone = telephone
            existing_patient.statut = 1

            if not existing_patient.email:
                existing_patient.email = email if email and not User.query.filter_by(email=email).first() else _generate_unique_patient_email()
            elif email and existing_patient.email != email and not User.query.filter_by(email=email).first():
                existing_patient.email = email

            if hasattr(existing_patient, "cin"):
                existing_patient.cin = cin

            db.session.commit()
            return jsonify(
                {
                    "message": "patient mis a jour avec succes",
                    "created": False,
                    "patient": {
                        "id": existing_patient.id,
                        "nom": existing_patient.nom,
                        "prenom": existing_patient.prenom,
                        "cin": existing_patient.cin,
                        "telephone": existing_patient.telephone,
                        "email": existing_patient.email,
                        "statut": existing_patient.statut,
                        "statut_label": USER_STATUS.get(existing_patient.statut, "patient"),
                    },
                }
            ), 200

        if not email or User.query.filter_by(email=email).first():
            email = _generate_unique_patient_email()

        patient = User(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            specialite=None,
            disponibilite=None,
            password="",
            access_code=None,
            statut=1,
        )

        if hasattr(patient, "cin"):
            patient.cin = cin

        db.session.add(patient)
        db.session.commit()

        return jsonify(
            {
                "message": "patient cree avec succes",
                "created": True,
                "patient": {
                    "id": patient.id,
                    "nom": patient.nom,
                    "prenom": patient.prenom,
                    "cin": patient.cin,
                    "telephone": patient.telephone,
                    "email": patient.email,
                    "statut": patient.statut,
                    "statut_label": USER_STATUS.get(patient.statut, "patient"),
                },
            }
        ), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/planning", methods=["GET"])
def get_medical_staff_planning():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        selected_date = parse_date(request.args.get("date")) or datetime.utcnow().date()

        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": f"Personnel #{id_personnel} introuvable"}), 404
        
        if not is_medical_staff(personnel):
            return jsonify({
                "error": f"L'utilisateur #{id_personnel} n'est pas du personnel medical (statut={personnel.statut}, specialite={personnel.specialite})"
            }), 403

        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)

        rdvs = (
            Rdv.query
            .filter(
                Rdv.idPersonnel == id_personnel,
                Rdv.dateRDV >= week_start,
                Rdv.dateRDV <= week_end,
            )
            .order_by(Rdv.dateRDV.asc(), Rdv.heureDebut.asc())
            .all()
        )

        grouped = {}
        for rdv in rdvs:
            day_key = rdv.dateRDV.isoformat()
            grouped.setdefault(day_key, []).append(
                {
                    "id": rdv.idRdv,
                    "idPatient": rdv.idPatient,
                    "idPersonnel": rdv.idPersonnel,
                    "dateRDV": rdv.dateRDV.isoformat(),
                    "heureDebut": rdv.heureDebut.strftime("%H:%M:%S"),
                    "heureFin": rdv.heureFin.strftime("%H:%M:%S"),
                    "motifConsultation": rdv.motifConsultation,
                    "statut": rdv.statut,
                    "patientNom": rdv.patient.nom if rdv.patient else "",
                    "patientPrenom": rdv.patient.prenom if rdv.patient else "",
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


@app.route("/medical-staff/patient-record", methods=["GET"])
def get_medical_staff_patient_record():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        id_patient = request.args.get("idPatient", type=int)
        current_rdv_id = request.args.get("currentRdvId", type=int)

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        patient = User.query.get(id_patient)
        if not patient:
            return jsonify({"error": "patient introuvable"}), 404

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
                    "id": rdv.idRdv,
                    "dateRDV": rdv.dateRDV.isoformat(),
                    "heureDebut": rdv.heureDebut.strftime("%H:%M:%S"),
                    "heureFin": rdv.heureFin.strftime("%H:%M:%S"),
                    "motifConsultation": rdv.motifConsultation,
                    "statut": rdv.statut,
                }
            )

        return jsonify(
            {
                "patient": {
                    "id": patient.id,
                    "nom": patient.nom,
                    "prenom": patient.prenom,
                    "telephone": patient.telephone,
                    "email": patient.email,
                    "statut": patient.statut,
                    "statut_label": USER_STATUS.get(patient.statut, "inconnu"),
                },
                "currentDoctorId": id_personnel,
                "historyCount": len(history),
                "lastAppointment": history[0] if history else None,
                "appointments": history,
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-full-profile", methods=["GET"])
def get_medical_staff_patient_full_profile():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        id_patient = request.args.get("idPatient", type=int)
        current_rdv_id = request.args.get("currentRdvId", type=int)

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        patient = User.query.get(id_patient)
        if not patient:
            return jsonify({"error": "patient introuvable"}), 404

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
                    "id": rdv.idRdv,
                    "dateRDV": rdv.dateRDV.isoformat(),
                    "heureDebut": rdv.heureDebut.strftime("%H:%M:%S"),
                    "heureFin": rdv.heureFin.strftime("%H:%M:%S"),
                    "motifConsultation": rdv.motifConsultation,
                    "statut": rdv.statut,
                }
            )

        health_fields = _get_patient_health_fields(id_patient)
        nom_complet = f"{(patient.prenom or '').strip()} {(patient.nom or '').strip()}".strip()

        return jsonify(
            {
                "patient": {
                    "id": patient.id,
                    "nom": patient.nom,
                    "prenom": patient.prenom,
                    "nomComplet": nom_complet or f"Patient #{patient.id}",
                    "cin": health_fields["cin"],
                    "sexe": health_fields["sexe"],
                    "telephone": patient.telephone,
                    "email": patient.email,
                    "statut": patient.statut,
                    "statut_label": USER_STATUS.get(patient.statut, "inconnu"),
                    "dateNaissance": health_fields["dateNaissance"],
                    "age": health_fields["age"],
                    "allergies": health_fields["allergies"],
                    "maladies": health_fields["maladies"],
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
def get_medical_staff_patients():
    try:
        id_personnel = request.args.get("idPersonnel", type=int)
        if not id_personnel:
            return jsonify({"error": "idPersonnel est obligatoire"}), 400

        personnel = User.query.get(id_personnel)
        if not personnel or not is_medical_staff(personnel):
            return jsonify({"error": "personnel medical introuvable"}), 404

        rows = (
            db.session.query(
                User.id,
                User.nom,
                User.prenom,
                User.email,
                User.telephone,
                db.func.count(Rdv.idRdv).label("rdvCount"),
            )
            .join(Rdv, Rdv.idPatient == User.id)
            .filter(Rdv.idPersonnel == id_personnel)
            .group_by(User.id, User.nom, User.prenom, User.email, User.telephone)
            .order_by(User.nom.asc(), User.prenom.asc())
            .all()
        )

        return jsonify([
            {
                "id": row.id,
                "nom": row.nom,
                "prenom": row.prenom,
                "email": row.email,
                "telephone": row.telephone,
                "rdvCount": int(row.rdvCount or 0),
            }
            for row in rows
        ]), 200
    except Exception as exc:
        return jsonify({"error": f"erreur serveur: {str(exc)}"}), 500


@app.route("/medical-staff/patient-full-profile/update", methods=["PUT"])
def update_medical_staff_patient_full_profile():
    try:
        data = request.get_json() or {}
        id_personnel = data.get("idPersonnel")
        id_patient = data.get("idPatient")
        payload = data.get("patient") or {}

        if not id_personnel or not id_patient:
            return jsonify({"error": "idPersonnel et idPatient sont obligatoires"}), 400

        personnel = User.query.get(int(id_personnel))
        if not personnel or not is_medical_staff(personnel):
            return jsonify({"error": "personnel medical introuvable"}), 404
        if not is_doctor(personnel):
            return jsonify({"error": "Seul le medecin peut modifier le profil patient"}), 403

        patient = User.query.get(int(id_patient))
        if not patient:
            return jsonify({"error": "patient introuvable"}), 404

        if payload.get("nom") is not None:
            patient.nom = str(payload.get("nom") or "").strip() or patient.nom
        if payload.get("prenom") is not None:
            patient.prenom = str(payload.get("prenom") or "").strip() or patient.prenom
        if payload.get("email") is not None:
            patient.email = str(payload.get("email") or "").strip() or None
        if payload.get("telephone") is not None:
            patient.telephone = str(payload.get("telephone") or "").strip() or None

        db.session.commit()

        _ensure_optional_user_columns()

        with db.engine.begin() as conn:
            existing_user_columns = {
                row[0]
                for row in conn.exec_driver_sql(
                    """
                    SELECT COLUMN_NAME
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'user'
                      AND COLUMN_NAME IN ('cin', 'sexe', 'genre', 'sex', 'date_naissance', 'allergies', 'maladies')
                    """
                ).fetchall()
            }

            updates = []
            params = {"id": int(id_patient)}

            if "cin" in existing_user_columns and payload.get("cin") is not None:
                updates.append("cin = %(cin)s")
                params["cin"] = str(payload.get("cin") or "").strip() or None

            sexe_value = payload.get("sexe")
            if sexe_value is not None:
                if "sexe" in existing_user_columns:
                    updates.append("sexe = %(sexe)s")
                    params["sexe"] = str(sexe_value).strip() or None
                elif "genre" in existing_user_columns:
                    updates.append("genre = %(sexe)s")
                    params["sexe"] = str(sexe_value).strip() or None
                elif "sex" in existing_user_columns:
                    updates.append("sex = %(sexe)s")
                    params["sexe"] = str(sexe_value).strip() or None

            if "date_naissance" in existing_user_columns and payload.get("dateNaissance") is not None:
                updates.append("date_naissance = %(date_naissance)s")
                params["date_naissance"] = parse_date(payload.get("dateNaissance"))

            if "allergies" in existing_user_columns and payload.get("allergies") is not None:
                value = payload.get("allergies")
                params["allergies"] = ", ".join(value) if isinstance(value, list) else str(value).strip()
                updates.append("allergies = %(allergies)s")

            if "maladies" in existing_user_columns and payload.get("maladies") is not None:
                value = payload.get("maladies")
                params["maladies"] = ", ".join(value) if isinstance(value, list) else str(value).strip()
                updates.append("maladies = %(maladies)s")

            if updates:
                conn.exec_driver_sql(
                    f"UPDATE user SET {', '.join(updates)} WHERE id = %(id)s",
                    params,
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

        if not id_personnel or not date_rdv:
            return jsonify({"error": "idPersonnel et dateRDV sont obligatoires"}), 400

        try:
            slot_duration = int(slot_duration)
        except (TypeError, ValueError):
            return jsonify({"error": "slotDuration doit etre un entier"}), 400

        if slot_duration <= 0:
            return jsonify({"error": "slotDuration doit etre superieur a 0"}), 400

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        plannings = (
            Planning.query
            .filter_by(idPersonnel=id_personnel, date=date_rdv)
            .order_by(Planning.heure_debut.asc())
            .all()
        )

        appointments = (
            Rdv.query
            .filter_by(idPersonnel=id_personnel, dateRDV=date_rdv)
            .order_by(Rdv.heureDebut.asc())
            .all()
        )

        booked_ranges = [(_to_minutes(r.heureDebut), _to_minutes(r.heureFin)) for r in appointments]

        planning_ranges = []
        for plan in plannings:
            planning_ranges.append((_to_minutes(plan.heure_debut), _to_minutes(plan.heure_fin)))

        # Fallback: if no planning is defined for the selected date, suggest slots on a default day window.
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
                    suggested_slots.append(
                        {
                            "heureDebut": _to_hhmmss(slot_start),
                            "heureFin": _to_hhmmss(slot_end),
                        }
                    )

                cursor += slot_duration

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
            "idPersonnel": int(id_personnel),
            "isUrgent": is_urgent,
            "slotDuration": slot_duration,
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
        
        print(f"    Parsed: patient={patient_nom} {patient_prenom}, personnel={id_personnel}, date={date_rdv}, time={heure_debut}-{heure_fin}, statut={statut}")

        if isinstance(statut, str):
            statut = statut.strip().lower()

        if not all([id_personnel, date_rdv, heure_debut, heure_fin, statut]):
            msg = f"Missing required fields: personnel={id_personnel}, date={date_rdv}, start={heure_debut}, end={heure_fin}, statut={statut}"
            print(f"    ERROR: {msg}")
            return jsonify({"error": "idPersonnel, dateRDV, heureDebut, heureFin et statut sont obligatoires"}), 400

        if statut not in RDV_CREATION_STATUTS:
            print(f"    ERROR: Invalid statut '{statut}', valid values: {RDV_CREATION_STATUTS}")
            return jsonify({"error": "statut invalide (consultation, controle)"}), 400

        patient = None
        if id_patient and int(id_patient) > 0:
            patient = User.query.get(id_patient)
            print(f"    Using existing patient ID {id_patient}")
        elif patient_nom and patient_prenom:
            # Generate unique email if not provided or if it already exists
            email = (data.get("email") or "").strip()
            if not email or User.query.filter_by(email=email).first():
                # Email is missing or already exists - generate a unique one
                email = _generate_unique_patient_email()
                print(f"    Generated unique email: {email}")
            
            patient = User(
                nom=patient_nom,
                prenom=patient_prenom,
                telephone=data.get("telephone"),
                email=email,
                specialite=None,
                disponibilite=None,
                statut=1,
                password="",
            )
            db.session.add(patient)
            db.session.flush()
            id_patient = patient.id
            print(f"    Created new patient ID {id_patient}: {patient_nom} {patient_prenom}")
        else:
            fallback_patient = User.query.filter_by(statut=1).order_by(User.id.asc()).first()
            if not fallback_patient:
                print(f"    ERROR: No fallback patient available")
                return jsonify({"error": "aucun patient disponible pour creer un RDV public"}), 400
            patient = fallback_patient
            id_patient = fallback_patient.id
            print(f"    Using fallback patient ID {id_patient}")

        personnel = User.query.get(id_personnel)

        if not patient:
            print(f"    ERROR: Patient not found")
            return jsonify({"error": "patient introuvable"}), 404

        if not personnel:
            print(f"    ERROR: Personnel not found")
            return jsonify({"error": "personnel introuvable"}), 404

        if not is_medical_staff(personnel):
            print(f"    ERROR: Personnel is not medical staff")
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

        # Check for appointment conflicts
        has_conflict, conflicting_rdv = check_appointment_conflict(id_personnel, date_rdv, heure_debut, heure_fin)
        if has_conflict and conflicting_rdv:
            conflict_info = {
                "heureDebut": conflicting_rdv.heureDebut.strftime("%H:%M:%S"),
                "heureFin": conflicting_rdv.heureFin.strftime("%H:%M:%S"),
                "patientNom": conflicting_rdv.patient.nom if conflicting_rdv.patient else "Inconnu",
                "patientPrenom": conflicting_rdv.patient.prenom if conflicting_rdv.patient else "",
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
            statut=statut,
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

        if "idPatient" in data:
            patient = User.query.get(data["idPatient"])
            if not patient:
                return jsonify({"error": "patient introuvable"}), 404
            rdv.idPatient = data["idPatient"]

        if "idPersonnel" in data:
            personnel = User.query.get(data["idPersonnel"])
            if not personnel:
                return jsonify({"error": "personnel introuvable"}), 404
            if not is_medical_staff(personnel):
                return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400
            rdv.idPersonnel = data["idPersonnel"]

        if "dateRDV" in data:
            parsed_date = parse_date(data.get("dateRDV"))
            if not parsed_date:
                return jsonify({"error": "dateRDV invalide (format YYYY-MM-DD)"}), 400
            rdv.dateRDV = parsed_date

        if "heureDebut" in data:
            parsed_start = parse_time(data.get("heureDebut"))
            if not parsed_start:
                return jsonify({"error": "heureDebut invalide (format HH:MM ou HH:MM:SS)"}), 400
            rdv.heureDebut = parsed_start

        if "heureFin" in data:
            parsed_end = parse_time(data.get("heureFin"))
            if not parsed_end:
                return jsonify({"error": "heureFin invalide (format HH:MM ou HH:MM:SS)"}), 400
            rdv.heureFin = parsed_end

        if "statut" in data:
            if data["statut"] not in RDV_STATUTS:
                return jsonify({"error": "statut invalide (urgence, consultation, controle)"}), 400
            rdv.statut = data["statut"]

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

        personnel = User.query.get(id_personnel)
        if not personnel:
            return jsonify({"error": "personnel introuvable"}), 404
        if not is_medical_staff(personnel):
            return jsonify({"error": "idPersonnel doit correspondre a un personnel medical"}), 400

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


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "API Flask MySQL operationnelle"}), 200


with app.app_context():
    db.create_all()
    migrate_mysql_schema()


if __name__ == "__main__":
    app.run(debug=True)

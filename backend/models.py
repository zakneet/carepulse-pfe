from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False, default='')
    role = db.Column(db.String(50), nullable=False, default='patient')
    specialite = db.Column(db.String(100))
    disponibilite = db.Column(db.String(500))
    
    # Relations
    patient_rdvs = db.relationship('RDV', foreign_keys='RDV.idPatient', backref='patient', lazy=True)
    personnel_rdvs = db.relationship('RDV', foreign_keys='RDV.idPersonnel', backref='personnel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'email': self.email,
            'role': self.role,
            'specialite': self.specialite,
            'disponibilite': self.disponibilite
        }


class RDV(db.Model):
    __tablename__ = 'rdv'
    
    idRDV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPatient = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    idPersonnel = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dateRDV = db.Column(db.Date, nullable=False, index=True)
    heureDebut = db.Column(db.Time, nullable=False)
    heureFin = db.Column(db.Time)
    motifConsultation = db.Column(db.String(500))
    statut = db.Column(db.String(50), default='Confirme')
    agePatient = db.Column(db.Integer)
    isUrgent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.idRDV,
            'idRDV': self.idRDV,
            'idPatient': self.idPatient,
            'idPersonnel': self.idPersonnel,
            'dateRDV': self.dateRDV.isoformat() if self.dateRDV else None,
            'heureDebut': self.heureDebut.isoformat() if self.heureDebut else None,
            'heureFin': self.heureFin.isoformat() if self.heureFin else None,
            'motifConsultation': self.motifConsultation,
            'statut': self.statut,
            'agePatient': self.agePatient,
            'isUrgent': self.isUrgent
        }


class AccessCode(db.Model):
    __tablename__ = 'access_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code_hash = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'code_hash': self.code_hash,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'description': self.description
        }

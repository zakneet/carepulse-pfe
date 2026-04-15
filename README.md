# CarePulse - Gestion des rendez-vous medicals

CarePulse est une application web full-stack de gestion des rendez-vous medicals. Le projet combine un frontend Angular et un backend Flask/MySQL pour permettre a un patient de reserver un rendez-vous, et au personnel medical de gerer le planning, les dossiers patients et les urgences.

## Apercu

L'application couvre les besoins suivants :

- creation et consultation des rendez-vous
- affichage du planning medical en temps reel
- detection des conflits de creneaux
- recherche et ouverture rapide du profil patient par CIN
- gestion des profils patients par le personnel medical
- mode urgence patient et urgence medecin
- authentification par role avec JWT

## Stack technique

- Frontend: Angular 13, TypeScript, RxJS, Bootstrap
- Backend: Flask 3, Flask-CORS, Flask-SQLAlchemy, PyMySQL, PyJWT
- Base de donnees: MySQL

## Fonctionnalites principales

### Cote patient

- creer un compte patient
- se connecter et acceder a son espace
- prendre un rendez-vous en choisissant un medecin et un creneau
- visualiser ses informations personnelles

### Cote medical staff

- consulter le planning journalier et hebdomadaire
- voir les rendez-vous par creneau
- ouvrir le dossier patient depuis le planning
- rechercher un patient par CIN dans le formulaire
- creer ou mettre a jour un patient avec statut `1`
- gerer les urgences patient et medecin

### Regles metier

- un rendez-vous ne peut pas chevaucher un autre creneau du meme medecin
- si un patient existe deja, son profil peut etre retrouve par CIN
- si un patient est cree depuis le formulaire medical, son statut est force a `1`
- les rendez-vous et patients valides sont enregistres en base de donnees

## Architecture rapide

- `frontend/` contient l'interface Angular
- `backend/` contient l'API Flask et la logique MySQL
- `backend/app.py` expose les routes REST principales
- `frontend/src/app/services/rdv.service.ts` centralise les appels API

## Prerequis

- Python 3.10+ recommande
- Node.js 16+ ou 18+ recommande
- Angular CLI 13
- MySQL 8 ou compatible

## Configuration de la base de donnees

Le backend utilise les variables suivantes :

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=gestion_des_rendez-vous
SECRET_KEY=dev-secret-key-change-in-prod
```

Si les variables ne sont pas definies, le backend utilise les valeurs par defaut ci-dessus.

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd pfe
```

### 2. Installer le backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Installer le frontend

```powershell
cd ..\frontend
npm install
```

## Lancement en local

Ouvre deux terminaux.

### Terminal 1 - Backend

```powershell
cd backend
.venv\Scripts\python.exe app.py
```

Le backend demarre par defaut sur :

```text
http://127.0.0.1:5000
```

### Terminal 2 - Frontend

```powershell
cd frontend
npm start
```

Le frontend Angular demarre par defaut sur :

```text
http://localhost:4200
```

## Flux d'utilisation

### Patient

1. Ouvrir l'application frontend.
2. Se connecter ou creer un compte.
3. Aller sur le formulaire de rendez-vous.
4. Choisir un medecin et un creneau disponible.
5. Valider la demande.

### Personnel medical

1. Se connecter avec un compte medical.
2. Ouvrir le planning.
3. Consulter les rendez-vous du jour ou de la semaine.
4. Ouvrir un dossier patient.
5. Rechercher un patient par CIN depuis le formulaire.
6. Creer ou mettre a jour un patient si le CIN n'existe pas.

## Endpoints principaux

### Authentification

- `POST /register`
- `POST /login`

### Rendez-vous

- `GET /rdvs`
- `GET /get_rdvs`
- `POST /add_rdv`
- `PUT /update_rdv/<id>`
- `DELETE /delete_rdv/<id>`

### Personnel medical

- `GET /medical-staff`
- `GET /medical-staff/planning`
- `GET /medical-staff/patients`
- `GET /medical-staff/patient-record`
- `GET /medical-staff/patient-full-profile`
- `POST /medical-staff/patient-save`
- `GET /medical-staff/patient-by-cin`

## Verification rapide

Tu peux tester le backend avec le script integre :

```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\backend
.venv\Scripts\python.exe test_e2e.py
```

Ou generer des RDV de test pour le planning :

```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\backend
.venv\Scripts\python.exe create_test_rdvs.py
```

## Structure du projet

```text
pfe/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── test_e2e.py
│   └── create_test_rdvs.py
├── frontend/
│   ├── src/app/
│   │   ├── medical-staff/
│   │   ├── patient/
│   │   ├── rdv-form/
│   │   └── services/
│   └── package.json
├── ARCHITECTURE.md
├── API_DOCUMENTATION.md
└── QUICK_START.md
```

## Notes importantes

- Le backend cree et met a jour la base via SQLAlchemy au demarrage.
- Les RDV valides sont persistants et apparaissent dans le planning medical.
- La logique de conflit empeche deux rendez-vous du meme medecin sur le meme creneau.
- Les patients crees depuis le formulaire medical recoivent automatiquement un statut `1`.

## Ameliorations possibles

- hashage des mots de passe avec bcrypt
- pagination des listes de patients et RDV
- notifications en temps reel
- export PDF du planning
- dashboard admin complet

## Auteur

Projet de fin d'etudes centre sur la gestion des rendez-vous medicals.


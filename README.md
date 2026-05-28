# OptiClinic - Plateforme de Gestion Médicale

OptiClinic (anciennement appelé CarePulse) est une application web full-stack dédiée à la gestion des rendez-vous médicaux et des dossiers patients. Le projet combine un frontend Angular moderne et un backend Flask/MySQL robuste pour permettre aux patients de gérer leurs rendez-vous et au personnel médical de gérer le planning, les dossiers et les urgences.

## 🌟 Aperçu du Projet

L'application couvre les besoins suivants :
- Création et consultation des rendez-vous (patients et personnel).
- Affichage du planning médical en temps réel avec gestion des conflits.
- Gestion complète des profils patients (recherche par CIN, mise à jour, création).
- Mode urgence pour les patients et les médecins.
- Authentification sécurisée par rôle avec JWT (Patient, Médecin, Administrateur).

## 🛠 Stack Technique

- **Frontend** : Angular 13, TypeScript, RxJS, Bootstrap, HTML/CSS
- **Backend** : Python 3.10+, Flask 3, Flask-SocketIO, Flask-CORS, Flask-SQLAlchemy, PyMySQL, PyJWT
- **Base de données** : MySQL 8

## ✨ Fonctionnalités Implémentées (Où nous en sommes)

### 1. Système d'Authentification (✅ Terminé)
- Connexion par rôle (Patient vs Personnel Médical).
- Le personnel médical nécessite un "Code d'Accès" sécurisé en plus du mot de passe.
- Sécurisation des routes Frontend avec `AuthGuard` et `RoleGuard`.
- Redirection intelligente post-connexion selon le rôle.
- Protection des API Backend via JWT token.

### 2. Espace Patient (✅ Opérationnel)
- Création de compte et connexion sécurisée.
- Prise de rendez-vous en choisissant un médecin et un créneau.
- Visualisation de ses informations personnelles et historique.

### 3. Espace Personnel Médical (✅ Opérationnel)
- Consultation du planning journalier et hebdomadaire.
- Visualisation des rendez-vous par créneau sans chevauchement.
- Recherche rapide et ouverture d'un dossier patient via CIN.
- Création/mise à jour d'un dossier patient.

### 4. Backend & API (✅ Robuste)
- Architecture modulaire et claire.
- Base de données MySQL structurée avec SQLAlchemy.
- Endpoints RESTful documentés pour l'authentification, les rendez-vous et la gestion des patients.

## 🚀 Comment lancer le projet (Guide de démarrage)

### Prérequis
- Python 3.10+
- Node.js 16+ ou 18+
- Angular CLI 13 (`npm install -g @angular/cli@13`)
- Serveur MySQL en cours d'exécution

### Configuration de la base de données
Assurez-vous d'avoir une base de données nommée `gestion_des_rendez-vous-3`. Le backend créera les tables automatiquement au démarrage.
Identifiants par défaut (modifiables via variables d'environnement) :
`Host: localhost`, `Port: 3306`, `User: root`, `Password: (vide)`

### 1️⃣ Lancer le Backend (Terminal 1)

Ouvrez un terminal PowerShell :

```powershell
cd backend

# Créer un environnement virtuel localement (seulement la première fois)
python -m venv .venv

# Autoriser l'activation de l'environnement virtuel
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Activer l'environnement virtuel
.\.venv\Scripts\activate

# Installer les dépendances (Flask, SocketIO, etc.) - Si ce n'est pas déjà fait
pip install -r requirements.txt

# Lancer l'application Flask
python app.py
```
Le backend démarrera sur `http://127.0.0.1:5000`.

### 2️⃣ Lancer le Frontend (Terminal 2)

Ouvrez un nouveau terminal :

```powershell
cd frontend

# Installer les packages (seulement la première fois)
npm install

# Démarrer le serveur de développement Angular
npm start
```
Le frontend sera accessible sur `http://localhost:4200`.

## 📁 Architecture du Code

- `/backend/` : Code source de l'API Flask, modèles SQLAlchemy, tests unitaires et scripts de migration.
- `/frontend/` : Application Angular contenant les modules `medical-staff`, `patient`, `rdv-form`, et `services`.
- `API_DOCUMENTATION.md` : Documentation détaillée des endpoints.
- `DELIVERY_CHECKLIST.md` : Suivi de la validation des spécifications.
- `QUICK_START.md` : Commandes et scripts rapides pour tester et initialiser des données.

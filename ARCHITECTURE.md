# 🏗️ ARCHITECTURE SYSTÈME - OptiClinic

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT (Navigateur)                  │
│                      localhost:4200                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Login Component                         │   │
│  │  - Sélecteur type utilisateur (onglets)             │   │
│  │  - Champ code d'accès (conditionnel)                │   │
│  │  - Validation frontend                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           AuthService (Observable)                  │   │
│  │  - Gestion JWT                                      │   │
│  │  - User State Management                            │   │
│  │  - Login/Logout                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          JwtInterceptor                             │   │
│  │  - Ajoute Authorization: Bearer {token}             │   │
│  │  - Détecte 401/403 → logout auto                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓ HTTP                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (Flask)                        │
│                   127.0.0.1:5000                            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │          POST /login                              │   │
│  │  Input: email, password, userType, accessCode     │   │
│  │  ├─ Validation email + password                   │   │
│  │  ├─ Si médical_staff:                             │   │
│  │  │  ├─ Vérifier code d'accès (hash comparison)    │   │
│  │  │  └─ Si invalide → HTTP 403                     │   │
│  │  ├─ Générer JWT token                             │   │
│  │  └─ Retourner token + user + role                 │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │       Validation & JWT Generation                 │   │
│  │  - Hash code d'accès vs storage                    │   │
│  │  - Role mapping (patient/doctor → patient/medical)│   │
│  │  - JWT: payload = {user_id, user_type, role}      │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓ Response
┌─────────────────────────────────────────────────────────────┐
│              Database (MySQL)                               │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │  users table     │      │  access_codes table      │   │
│  │  ├─ id*          │      │  ├─ id*                  │   │
│  │  ├─ email        │      │  ├─ code_hash           │   │
│  │  ├─ password     │      │  ├─ user_type           │   │
│  │  ├─ nom          │      │  ├─ is_active           │   │
│  │  ├─ prenom       │      │  ├─ created_at          │   │
│  │  ├─ role         │      │  └─ description         │   │
│  │  └─ ...          │      └──────────────────────────┘   │
│  └──────────────────┘                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Flux Authentication

### Patient

```
START
  ↓
[User navigates to /]
  ↓
[Router checks isAuthenticated()]
  ├─ NO → Redirect /login
  │         ↓
  │     [Display Login Page]
  │         ↓
  │     [Select Type: Patient]
  │         ↓
  │     [Enter Email & Password]
  │         ↓
  │     [Code d'accès field: HIDDEN]
  │         ↓
  │     [Click "Se connecter"]
  │         ↓
  │     AuthService.login({
  │       email,
  │       password,
  │       userType: 'patient'
  │     })
  │         ↓
  │     [HTTP POST /login]
  │         ↓
  │     Backend:
  │     ├─ Check email + password
  │     ├─ Find user
  │     ├─ Generate JWT
  │     └─ Return token + user
  │         ↓
  │     [Store in localStorage]
  │     ├─ authToken = jwt
  │     └─ authUser = {id, nom, prenom, email, role}
  │         ↓
  │     [Redirect /patient/dashboard]
  │         ↓
  └─ YES → Redirect appropriate dashboard
           (based on user role)

END
```

### Medical Staff (avec code d'accès)

```
START
  ↓
[User navigates to /]
  ↓
[Router checks isAuthenticated()]
  ├─ NO → Redirect /login
  │         ↓
  │     [Display Login Page]
  │         ↓
  │     [Select Type: Médecin]
  │         ↓
  │     [Enter Email & Password]
  │         ↓
  │     [Code d'accès field: VISIBLE ⭐]
  │         ↓
  │     [Enter Code d'accès (required)]
  │         ↓
  │     Frontend validation:
  │     ├─ Check all fields filled
  │     └─ If any empty → Error
  │         ↓
  │     [Click "Se connecter"]
  │         ↓
  │     AuthService.login({
  │       email,
  │       password,
  │       userType: 'doctor',
  │       accessCode: 'DOCTOR2024SECRET'
  │     })
  │         ↓
  │     [HTTP POST /login]
  │         ↓
  │     Backend:
  │     ├─ Check email + password
  │     ├─ User exists?
  │     ├─ userType is medical_staff? YES
  │     ├─ accessCode provided? NO → Error 403
  │     ├─ Get code_hash from access_codes table
  │     ├─ hash(input) == hash(stored)?
  │     │  NO → Error 403 "Code invalide"
  │     │  YES → Continue
  │     ├─ Generate JWT
  │     │  payload: {user_id, user_type: 'doctor', role: 'medical_staff'}
  │     └─ Return token + user + role
  │         ↓
  │     [Store in localStorage]
  │     ├─ authToken = jwt
  │     └─ authUser = {..., role: 'medical_staff'}
  │         ↓
  │     [Redirect /medical-staff/dashboard]
  │         ↓
  └─ YES → RoleGuard checks role:
           ├─ patient → /patient/dashboard
           └─ medical_staff → /medical-staff/dashboard

END
```

---

## Flux Protection des Routes

### AuthGuard (Check if authenticated)

```
User requests protected route
         ↓
AuthGuard.canActivate()
         ↓
authService.isAuthenticated()?
    ├─ YES → Allow access
    │         ↓
    │     Component loads
    │
    └─ NO → Redirect /login
            with queryParam: returnUrl
```

### RoleGuard (Check if correct role)

```
User authenticated, requests route
         ↓
RoleGuard.canActivate()
         ↓
Check route.data['roles']
         ↓
userRole in allowedRoles?
    ├─ YES → Allow access
    │         ↓
    │     Component loads
    │
    └─ NO → Redirect to role dashboard
            ├─ patient → /patient/dashboard
            ├─ medical_staff → /medical-staff/dashboard
            └─ admin → /admin/dashboard
```

---

## Modèle de Données

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),           -- ⚠️ TODO: Ajouter bcrypt
    telephone VARCHAR(20),
    role INT DEFAULT 1,              -- 1=patient, 2=medical, 3=admin
    specialite VARCHAR(100),
    disponibilite TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Access Codes Table
```sql
CREATE TABLE access_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_hash VARCHAR(255) NOT NULL UNIQUE,  -- SHA256 encrypted
    user_type VARCHAR(50),                    -- 'doctor', 'laboratory', 'other_staff'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,           -- Soft delete
    description VARCHAR(255)
);
```

---

## État d'Authentification (localStorage)

```javascript
// Après login réussi
localStorage = {
    authToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJ1c2VyX3R5cGUiOiJwYXRpZW50Iiwicm9sZSI6InBhdGllbnQifQ.LIn9SMBMiRi6GW7SwHrqnRkoBLwBdqNxZaKnddRPOZY",
    authUser: {
        "id": 5,
        "nom": "Testeur",
        "prenom": "Patient",
        "email": "patient.test@example.com",
        "role": "patient",
        "userType": "patient"
    }
}

// Après logout
localStorage = {}  // Vide
```

---

## Flux Interceptor

```
User makes HTTP request
         ↓
JwtInterceptor intercepts
         ↓
Get token from authService.getToken()
         ↓
token exists?
    ├─ YES → Add header:
    │        Authorization: Bearer {token}
    │
    └─ NO → Send as-is

         ↓
Request sent to backend
         ↓
Response received
         ↓
Status code check:
    ├─ 401 (Unauthorized) → logout() + redirect /login
    ├─ 403 (Forbidden) → logout() + redirect /login
    └─ Otherwise → Continue
```

---

## Rôles et Permissions

| Feature | Patient | Médecin | Labo | Autre Staff | Admin |
|---------|---------|---------|------|-------------|-------|
| Login sans code | ✓ | ✗ | ✗ | ✗ | ✓(tbd) |
| Code d'accès | ✗ | ✓ | ✓ | ✓ | ✗ |
| Dashboard propre | ✓ | ✓ | ✓ | ✓ | ✓ |
| Voir RDVs | ✓ | ✓ | ✓ | ✓ | ✓ |
| Créer RDV | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gérer codes accès | ✗ | ✗ | ✗ | ✗ | ✓ |
| Voir stats | Limité | ✓ | ✓ | ✓ | ✓ |

---

## Fichiers du Système

```
Source/
├── Angular Frontend
│   ├── models/
│   │   └── auth.model.ts
│   ├── services/
│   │   ├── auth.service.ts
│   │   └── rdv.service.ts
│   ├── guards/
│   │   ├── auth.guard.ts
│   │   └── role.guard.ts
│   ├── interceptors/
│   │   └── jwt.interceptor.ts
│   ├── login/
│   │   ├── login.component.ts
│   │   ├── login.component.html
│   │   └── login.component.css
│   ├── medical-staff/
│   │   ├── medical-staff.module.ts
│   │   ├── medical-staff-routing.module.ts
│   │   └── components/
│   │       └── dashboard/
│   │           ├── .ts/.html/.css
│   ├── app.module.ts (modifié)
│   └── app-routing.module.ts (modifié)
│
└── Flask Backend
    ├── app.py (refactorisé)
    ├── requirements.txt
    └── test-api.ps1
```

---

**Architecture Complète et Documentée ✓**

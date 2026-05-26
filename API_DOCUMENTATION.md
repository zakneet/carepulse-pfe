# 📡 API ENDPOINTS DOCUMENTATION - OptiClinic

## Base URL
```
http://127.0.0.1:5000
```

---

## 🔐 AUTHENTIFICATION

### POST /register
**Créer un nouvel utilisateur**

**Request:**
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "password": "password123",
  "telephone": "0123456789",
  "role": 1,
  "specialite": null,
  "disponibilite": null
}
```

**Response (201):**
```json
{
  "message": "Compte créé avec succès"
}
```

**Errors:**
- `400` - Email déjà utilisé
- `400` - Champs obligatoires manquants

---

### POST /login
**Authentifier un utilisateur**

**Request (Patient):**
```json
{
  "email": "patient@example.com",
  "password": "password123",
  "userType": "patient"
}
```

**Request (Personnel Médical):**
```json
{
  "email": "doctor@example.com",
  "password": "password123",
  "userType": "doctor",
  "accessCode": "DOCTOR2024SECRET"
}
```

**Response (200):**
```json
{
  "message": "Connexion reussie",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 5,
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "role": "patient",
    "userType": "patient"
  }
}
```

**Errors:**
- `400` - Email ou password manquant
- `403` - Code d'accès obligatoire (personnel médical)
- `403` - Code d'accès invalide
- `401` - Email ou mot de passe incorrect

**User Types Acceptés:**
- `patient`
- `doctor`
- `laboratory`
- `other_staff`
- `admin`

**Rôles Retournés:**
- `patient` → patient
- `doctor` → medical_staff
- `laboratory` → medical_staff
- `other_staff` → medical_staff
- `admin` → admin

---

## 🔑 GESTION DES CODES D'ACCÈS (Admin)

### POST /admin/access-codes
**Créer un nouveau code d'accès**

**Request:**
```json
{
  "code": "DOCTOR2024SECRET",
  "user_type": "doctor",
  "description": "Code pour médecins - Valide jusqu'en 2024"
}
```

**Response (201):**
```json
{
  "message": "Code d'accès créé avec succès"
}
```

**Errors:**
- `400` - Ce code existe déjà
- `400` - Champs obligatoires manquants

**User Types Acceptés:**
- `doctor`
- `laboratory`
- `other_staff`

---

### POST /admin/access-codes/{id}/deactivate
**Désactiver un code d'accès**

**URL Parameters:**
- `id` (integer) - ID du code à désactiver

**Response (200):**
```json
{
  "message": "Code d'accès désactivé"
}
```

**Errors:**
- `404` - Code non trouvé

---

## 📅 RENDEZ-VOUS

### GET /get_rdvs
**Récupérer tous les rendez-vous**

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
```

**Response (200):**
```json
[
  {
    "id": 1,
    "idPatient": 5,
    "idPersonnel": 2,
    "dateRDV": "2026-03-28",
    "heureDebut": "09:30:00",
    "heureFin": "10:00:00",
    "motifConsultation": "Consultation générale",
    "statut": "Confirmé"
  }
]
```

---

### POST /add_rdv
**Créer un nouveau rendez-vous**

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "idPatient": 5,
  "idPersonnel": 2,
  "dateRDV": "2026-03-28",
  "heureDebut": "09:30",
  "heureFin": "10:00",
  "motifConsultation": "Consultation générale"
}
```

**Response (201):**
```json
{
  "message": "RDV enregistré avec succès"
}
```

---

### PUT /update_rdv/{id}
**Modifier un rendez-vous**

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "dateRDV": "2026-03-29",
  "heureDebut": "14:00",
  "motifConsultation": "Consultation modifiée"
}
```

**Response (200):**
```json
{
  "message": "RDV mis à jour"
}
```

---

### DELETE /delete_rdv/{id}
**Supprimer un rendez-vous**

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
```

**Response (200):**
```json
{
  "message": "RDV supprimé"
}
```

---

## 🧪 TESTS

### GET /test_connection
**Tester la connexion à la base de données**

**Response (200):**
```json
{
  "message": "Connexion MySQL OK"
}
```

---

## 🔒 AUTHENTIFICATION JWT

### Format du Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{payload}.{signature}
```

### Payload
```json
{
  "user_id": 5,
  "user_type": "patient",
  "role": "patient"
}
```

### Utilisation
Ajouter le token à chaque requête protégée :
```
Authorization: Bearer {token}
```

### Durée de Vie
- Pas de limite d'expiration pour le moment (À CHANGER EN PRODUCTION)
- Recommandation : 1 heure d'expiration + refresh token

---

## ⚠️ ERREURS COURANTES

### 401 Unauthorized
```json
{
  "error": "Email ou mot de passe incorrect"
}
```
**Solution:** Vérifier email et password

### 403 Forbidden
```json
{
  "error": "Le code d'accès est obligatoire pour le personnel médical"
}
```
**Solution:** Ajouter le champ `accessCode` pour les médecins

```json
{
  "error": "Code d'accès invalide"
}
```
**Solution:** Vérifier que le code d'accès est correct et actif

### 400 Bad Request
```json
{
  "error": "email et password sont obligatoires"
}
```
**Solution:** Vérifier que tous les champs obligatoires sont présents

---

## 🧩 INTÉGRATION FRONTEND

### AuthService Usage
```typescript
// Login
this.authService.login({
  email: 'patient@example.com',
  password: 'password123',
  userType: 'patient'
}).subscribe(user => {
  console.log('Connecté !', user);
});

// Logout
this.authService.logout();

// Vérifier authentification
if (this.authService.isAuthenticated()) {
  console.log('Utilisateur connecté');
}

// Vérifier rôle
if (this.authService.isPatient()) {
  console.log('Accès patient');
}
if (this.authService.isMedicalStaff()) {
  console.log('Accès médical');
}
```

### Guards Usage
```typescript
// Dans app-routing.module.ts
{
  path: 'patient',
  canActivate: [AuthGuard, RoleGuard],
  data: { roles: [UserRole.PATIENT] },
  component: PatientComponent
}
```

---

**Documentation APIs - COMPLETE ✓**

# 🔐 Système de Code d'Accès - Personnel Médical

## 📋 Résumé

Le système d'authentification du projet intègre un **code d'accès sécurisé** pour le personnel médical (Médecins et Nurses). Cette couche de sécurité supplémentaire garantit que seul le personnel autorisé peut accéder à l'interface médicale.

---

## 🎯 Fonctionnalités

### Pour le Personnel Médical
- ✅ Accès rapide sans email/mot de passe
- ✅ Code d'accès unique par personne
- ✅ Code alphanumérique (6 caractères par défaut)
- ✅ Validation normalisée (insensible aux espaces et casse)

### Pour les Patients
- ✅ Authentification classique (email + mot de passe)
- ✅ Pas d'impact sur le flux patient

---

## 🚀 Configuration des Codes d'Accès

### 1️⃣ Afficher les Codes Existants

```bash
cd backend
python show_access_codes.py
```

**Sortie attendue:**
```
================================================================================
🔐 CODES D'ACCÈS - PERSONNEL MÉDICAL
================================================================================

✅ DUPONT JEAN
   ID: 1
   Type: Medecin
   Code: DR2024
   Email: jean.dupont@clinic.fr

❌ MARTIN MARIE
   ID: 2
   Type: Secretaire
   Code: Non configuré
   Email: marie.martin@clinic.fr
```

### 2️⃣ Configurer les Codes d'Accès

```bash
cd backend
python setup_access_codes.py
```

Le script vous guidera interactivement:
- Liste chaque personnel médical
- Propose de générer automatiquement un code
- Permet de garder un code existant
- Permet de saisir un code personnalisé

**Exemple d'interaction:**
```
👤 DUPONT JEAN
   ID: 1
   Type: medecin
   Email: jean.dupont@clinic.fr
   🔑 Code généré: AB12CD
   Confirmer ce code ? (O/N) [O]: O
```

---

## 🔑 Structure de la Base de Données

### Table `personnel_de_sante`

```sql
CREATE TABLE personnel_de_sante (
    id_personnel INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(120) UNIQUE,
    type_personnel VARCHAR(50),  -- 'medecin' ou 'secretaire'
    access_code VARCHAR(120) UNIQUE,  -- Code d'accès pour l'authentification
    specialite VARCHAR(120),
    statut INT DEFAULT 2,
    ...
)
```

**Champs clés:**
- `access_code`: Code d'accès unique (nullable)
- `type_personnel`: Détermine le type de personnel

---

## 🔄 Flux d'Authentification

### 1. Écran Initial (Login)

L'utilisateur accède à `/login` et voit deux options:
```
┌─────────────────────────────────────┐
│  Choisissez votre profil            │
├─────────────────────────────────────┤
│  ○ Patient                          │
│  ○ Personnel de santé               │
└─────────────────────────────────────┘
```

### 2. Sélection: Personnel de Santé

Le formulaire affiche un champ pour le **code d'accès**:
```
┌─────────────────────────────────────┐
│  Connexion Personnel de santé       │
├─────────────────────────────────────┤
│  Code d'accès: [**********]         │
│  [Se connecter]                     │
│  [Changer de profil]                │
└─────────────────────────────────────┘
```

### 3. Validation Backend

**Endpoint:** `POST /login`

**Requête:**
```json
{
  "userType": "medical_staff",
  "accessCode": "AB12CD"
}
```

**Logique de validation:**
1. Récupère le code depuis la requête
2. Normalise le code (supprime espaces, minuscules)
3. Compare avec les codes de la base de données
4. Retourne un JWT token si valide

**Réponse (Succès):**
```json
{
  "message": "Connexion réussie",
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "nom": "DUPONT",
    "prenom": "Jean",
    "role": "medecin",
    "userType": "medical_staff",
    "type_personnel": "medecin"
  }
}
```

**Réponse (Erreur):**
```json
{
  "error": "code d'acces invalide (ou non configure pour ce personnel)"
}
```

### 4. Accès à l'Interface

Une fois authentifié, le personnel accède à:
- `/medical-staff/dashboard` - Tableau de bord
- `/medical-staff/patients` - Liste des patients
- `/medical-staff/appointments` - Gestion des RDV
- Autres routes protégées par `@require_medical_staff`

---

## 🛡️ Sécurité

### Points Forts
- ✅ Code d'accès unique par personnel
- ✅ Validation côté backend
- ✅ JWT token avec expiration
- ✅ Normalization du code (anti-bypass)
- ✅ Base de données: `access_code` en UNIQUE KEY

### Bonnes Pratiques
- 🔒 Codes générés aléatoirement (6 caractères min)
- 🔒 Codes alphanumérique (lettres + chiffres)
- 🔒 Pas de transmission du code en clair via API (HTTPS obligatoire)
- 🔒 Codes stockés en base (pas de hachage spécifique, dépend de votre politique)

### Recommandations
1. **Utiliser HTTPS en production** - Tous les codes d'accès doivent transiter en HTTPS
2. **Modifier les codes régulièrement** - Renouveler tous les 3-6 mois
3. **Conserver les codes de manière sécurisée** - Format papier verrouillé ou gestionnaire de secrets
4. **Logger les authentifications** - Tracer qui se connecte et quand
5. **Désactiver les codes expirés** - Supprimer les codes des personnel partis

---

## 📲 Interface Frontend (Angular)

### Composant: `login.component.ts`

**Propriétés:**
```typescript
selectedUserType: UserType | null = null;
credentials = {
  email: '',
  password: '',
  accessCode: ''  // Pour le personnel médical
};
```

**Logique:**
```typescript
isMedicalStaffUserType(): boolean {
  return this.selectedUserType === UserType.MEDICAL_STAFF;
}

login(): void {
  if (this.isMedicalStaffUserType()) {
    // Mode code d'accès
    const loginRequest = {
      userType: "medical_staff",
      accessCode: this.credentials.accessCode
    };
  } else {
    // Mode email + mot de passe
    const loginRequest = {
      userType: "patient",
      email: this.credentials.email,
      password: this.credentials.password
    };
  }
  // ...
}
```

### Modèle: `auth.model.ts`

```typescript
export interface LoginRequest {
  userType: UserType;
  email?: string;
  password?: string;
  accessCode?: string;  // Pour medical_staff
}

export enum UserType {
  PATIENT = 'patient',
  MEDICAL_STAFF = 'medical_staff'
}
```

---

## 🔧 Modification du Système

### Changer la Longueur du Code

Fichier: `backend/setup_access_codes.py`

```python
def generate_access_code(length=6):  # Modifiez cette valeur
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
```

### Ajouter des Caractères Spéciaux

```python
def generate_access_code(length=8):
    characters = string.ascii_uppercase + string.digits + "!@#$%"
    return ''.join(random.choice(characters) for _ in range(length))
```

### Charger des Codes Depuis un Fichier CSV

Créer `backend/load_access_codes.py`:
```python
import csv
from app import app, db, PersonnelDeSante

def load_from_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)  # Colonnes: id_personnel, access_code
        for row in reader:
            staff = PersonnelDeSante.query.get(row['id_personnel'])
            if staff:
                staff.access_code = row['access_code']
    db.session.commit()
```

---

## 🐛 Dépannage

### Problème: "Code d'accès invalide"

**Causes possibles:**
- ❌ Code incorrect
- ❌ Code non configuré dans la base de données
- ❌ Espaces dans le code
- ❌ Différence de casse

**Solutions:**
```bash
# Vérifier les codes existants
python show_access_codes.py

# Reconfigurer les codes
python setup_access_codes.py
```

### Problème: Impossible de se connecter après configuration

**Vérifier:**
1. Backend en cours d'exécution: `python app.py`
2. MySQL accessible: `mysql -u root -p gestion_des_rendez-vous`
3. Code dans la base de données:
   ```sql
   SELECT id_personnel, nom, prenom, access_code FROM personnel_de_sante;
   ```

### Problème: Code d'accès accepte aussi d'autres codes

**Cause:** Fonction `normalize_access_code()` trop permissive

**Fichier:** `backend/app.py`
```python
def normalize_access_code(value: str) -> str:
    return "".join(str(value or "").strip().split()).lower()
    # Supprime espaces et minuscules
```

---

## 📊 Statistiques

### Exemple de Configuration Complète

| Personnel | Type | ID | Code | Status |
|-----------|------|-----|------|--------|
| DUPONT Jean | Médecin | 1 | AB12CD | ✅ Actif |
| MARTIN Marie | Secrétaire | 2 | XY34ZZ | ✅ Actif |
| BERNARD Luc | Médecin | 3 | 98PASS | ✅ Actif |
| RICHARD Sophie | Infirmière | 4 | NS55AA | ✅ Actif |

---

## 🎓 Tutoriel Complet

### Étape 1: Vérifier les Personnels Existants
```bash
python show_access_codes.py
```

### Étape 2: Générer les Codes d'Accès
```bash
python setup_access_codes.py
# Suivez les instructions interactives
```

### Étape 3: Vérifier la Configuration
```bash
python show_access_codes.py
# Tous les codes doivent être visibles
```

### Étape 4: Tester via l'Interface
1. Aller sur `http://localhost:4200/login`
2. Sélectionner "Personnel de santé"
3. Saisir le code d'accès (ex: AB12CD)
4. Cliquer "Se connecter"
5. Redirection vers le dashboard médical

---

## 📞 Support

Pour des questions ou issues, consultez:
- Documentation API: `API_DOCUMENTATION.md`
- Architecture système: `ARCHITECTURE.md`
- Guide de démarrage: `QUICK_START.md`

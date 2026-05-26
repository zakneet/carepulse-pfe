# 🚀 GUIDE DE DÉMARRAGE RAPIDE - OptiClinic

## ⚡ Démarrage en 5 minutes

### 1. Ouvrir 2 terminaux

**Terminal 1 - Backend Flask:**
```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\backend
python app.py
```

**Terminal 2 - Frontend Angular:**
```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\frontend
ng serve --port 4200
```

### 2. Ouvrir le navigateur

```
http://localhost:4200
```

→ **Redirection automatique vers `/login`**

---

## 👤 Tester Patient

### Créer un compte patient

1. Cliquer sur "Créer un compte"
2. Remplir le formulaire
3. Mot de passe stocké en clair (⚠️ TODO: bcrypt)

### Se connecter en tant que Patient

1. **Type :** Patient
2. **Email :** patient.test@example.com
3. **Password :** password123
4. **Code d'accès :** ❌ Ne pas remplir
5. Cliquer "Se connecter"

✓ **Redirection → `/patient/dashboard`**

---

## 👨‍⚕️ Tester Médecin

### Créer un code d'accès médecin

Ouvrir un terminal et exécuter :

```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\backend

$codeData = @{
    code = "DOCTOR2024SECRET"
    user_type = "doctor"
    description = "Code de test pour médecins"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:5000/admin/access-codes" `
    -Method POST `
    -ContentType "application/json" `
    -Body $codeData `
    -UseBasicParsing
```

Ou utiliser le script de test :

```powershell
.\test-api.ps1
```

### Se connecter en tant que Médecin

1. **Type :** Médecin
2. **Email :** patient.test@example.com (même utilisateur)
3. **Password :** password123
4. **Code d'accès :** `DOCTOR2024SECRET`
5. Cliquer "Se connecter"

✓ **Redirection → `/medical-staff/dashboard`**

---

## 🧪 Tester l'API Complètement

```powershell
cd C:\Users\NAHLA GLMK\Desktop\nadouna\pfe\backend
.\test-api.ps1
```

Résultats attendus :
- ✓ Connexion MySQL OK
- ✓ Créer compte patient OK
- ✓ Login patient OK (JWT obtenu)
- ✓ Login médecin sans code → REJETÉ (403)
- ✓ Créer code d'accès OK
- ✓ Login médecin avec code → OK (JWT obtenu)
- ✓ GET RDVs avec token → OK

---

## 🔍 Vérifier le JWT dans le Navigateur

### Ouvrir les outils développeur

`F12` → **Application** → **localStorage**

Vérifier les clés :
```
authToken    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
authUser     = '{"id": 5, "nom": "Testeur", ...}'
```

---

## ❌ Tester les Erreurs

### Patient essayant d'accéder au dashboard médecin

1. Login en tant que patient
2. Essayer d'accéder à `/medical-staff/dashboard`
3. ❌ **Redirection → `/login`** (RoleGuard)

### Médecin avec code invalide

1. **Type :** Médecin
2. **Email :** patient.test@example.com
3. **Password :** password123
4. **Code d'accès :** `INVALID_CODE`
5. ❌ **Message d'erreur :** "Code d'accès invalide"

### Accès sans authentification

1. Ouvrir `http://localhost:4200/patient/dashboard`
2. ❌ **Redirection → `/login`** (AuthGuard)

---

## 📋 RÔLES ET PERMISSIONS

| Rôle | Type | Code d'accès | Dashboard |
|------|------|--------------|-----------|
| Patient | `patient` | ❌ Non | `/patient/dashboard` |
| Médecin | `doctor` | ✅ Oui | `/medical-staff/dashboard` |
| Laboratoire | `laboratory` | ✅ Oui | `/medical-staff/dashboard` |
| Autre personnel | `other_staff` | ✅ Oui | `/medical-staff/dashboard` |
| Admin | `admin` | (À définir) | `/admin/dashboard` |

---

## 🐛 DÉPANNAGE

### Le serveur Flask ne démarre pas

```
❌ Module PyJWT not found
```

**Solution :**
```powershell
& "c:/Users/NAHLA GLMK/Desktop/nadouna/pfe/.venv/Scripts/pip.exe" install PyJWT
```

### Le port 4200 est déjà utilisé

```
❌ Port 4200 is already in use
```

**Solution - Killer le processus :**
```powershell
Get-NetTCPConnection -LocalPort 4200 | ForEach-Object { 
    Stop-Process -Id $_.OwningProcess -Force 
}
```

### JWT invalide / localStorage effacé

```
❌ Utilisateur redirectionné à /login
```

**Solution :** 
- Rafraîchir la page (`Ctrl+F5`)
- Se reconnecter
- JWT sera régénéré

### Erreur "Unread result found"

```
❌ {"error": "Unread result found"}
```

**Solution :** Ce bug a été corrigé dans la version actuelle. Si toujours présent :
- Redémarrer les serveurs
- Vérifier que tous les curseurs sont `.close()`

---

## 📊 STRUCTURE DE RÉPERTOIRES

```
nadouna/pfe/
├── frontend/
│   ├── src/app/
│   │   ├── models/
│   │   │   └── auth.model.ts
│   │   ├── services/
│   │   │   ├── auth.service.ts
│   │   │   └── rdv.service.ts
│   │   ├── guards/
│   │   │   ├── auth.guard.ts
│   │   │   └── role.guard.ts
│   │   ├── interceptors/
│   │   │   └── jwt.interceptor.ts
│   │   ├── login/
│   │   ├── medical-staff/
│   │   │   └── components/dashboard/
│   │   └── app-routing.module.ts
│   └── package.json
└── backend/
    ├── app.py (refactorisé)
    ├── requirements.txt
    ├── test-api.ps1
    └── test-api.sh
```

---

## 🎯 PROCHAINES ÉTAPES

### Court terme (À faire bientôt)
- [ ] Mot de passe hashé (bcrypt) au lieu de texte clair
- [ ] Tokens JWT avec expiration (1 heure)
- [ ] Refresh tokens
- [ ] 2FA optionnel
- [ ] Logs des authentifications

### Moyen terme
- [ ] Dashboard Admin complet
- [ ] Gestion des utilisateurs
- [ ] Gestion des codes d'accès depuis UI
- [ ] Notifications
- [ ] Calendar RDVs

### Long terme
- [ ] Mobile App
- [ ] API REST pour tiers
- [ ] OAuth2 integration
- [ ] Dossiers médicaux électroniques
- [ ] Prescription management

---

## 📞 BESOIN D'AIDE ?

### Vérifier les logs
- **Frontend :** Console navigateur (F12)
- **Backend :** Terminal Flask

### Fichiers de documentation
- `AUTHENTICATION_SUMMARY.md` - Vue d'ensemble complète
- `API_DOCUMENTATION.md` - Toutes les endpoints
- Ce fichier - Démarrage rapide

### Commandes utiles
```powershell
# Voir les ports utilisés
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in 4200, 5000 }

# Relancer le backend
cd backend; python app.py

# Relancer le frontend
cd frontend; ng serve --port 4200

# Tests API
cd backend; .\test-api.ps1
```

---

**PRÊT ? Bonne développement ! 🚀**

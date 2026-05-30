# 🔐 Guide Rapide: Code d'Accès Médical

## ✅ État du Système

Votre système est **OPÉRATIONNEL** ! ✨

- ✅ 4 personnels médicaux configurés avec codes d'accès
- ✅ Codes d'accès uniques pour chaque médecin/infirmière
- ✅ Système de validation en place

---

## 📋 Personnels Médical(aux) Actuels

| Nom | Prénom | Type | Code d'Accès |
|-----|--------|------|-------------|
| TESTDOCTOR | Med | Médecin | DOCD582EF0B |
| DUPONT | Jean | Médecin | STAFF2026 |
| DR | Test | Médecin | DOC2026 |
| DR | New | Médecin | CHIRURG2026 |

---

## 🚀 Démarrage Rapide

### 1️⃣ Vérifier les Codes d'Accès

```bash
cd backend
python verify_access_codes.py
```

Affiche l'état de tous les codes configurés.

### 2️⃣ Afficher les Codes d'Accès

```bash
cd backend
python show_access_codes.py
```

```
================================================================================
🔐 CODES D'ACCÈS - PERSONNEL MÉDICAL
================================================================================

✅ TESTDOCTOR MED
   ID: 1
   Type: Medecin
   Code: DOCD582EF0B
   Email: testdoctor@clinic.fr
```

### 3️⃣ Configurer/Modifier les Codes

```bash
cd backend
python setup_access_codes.py
```

Guide interactif pour :
- Générer automatiquement des codes
- Garder les codes existants
- Saisir des codes personnalisés

---

## 🧪 Tester l'Authentification

### Via l'Interface Web

1. **Ouvrez le navigateur:**
   ```
   http://localhost:4200/login
   ```

2. **Sélectionnez "Personnel de santé"**

3. **Saisissez un code d'accès:**
   ```
   DOCD582EF0B
   ```

4. **Cliquez "Se connecter"**

5. **Redirection automatique vers le dashboard** ✅

### Via cURL (API)

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "userType": "medical_staff",
    "accessCode": "DOCD582EF0B"
  }'
```

**Réponse (Succès):**
```json
{
  "message": "Connexion reussie",
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "nom": "TESTDOCTOR",
    "prenom": "Med",
    "role": "medecin",
    "userType": "medical_staff"
  }
}
```

---

## 🔒 Codes d'Accès Actuels

Utilisez ces codes pour tester:

| Médecin | Code | Description |
|---------|------|-------------|
| TESTDOCTOR Med | `DOCD582EF0B` | Médecin test principal |
| DUPONT Jean | `STAFF2026` | Médecin secondaire |
| DR Test | `DOC2026` | Médecin de test |
| DR New | `CHIRURG2026` | Chirurgien |

---

## 🛠️ Commandes Utiles

### Afficher tous les codes
```bash
python show_access_codes.py
```

### Vérifier la configuration
```bash
python verify_access_codes.py
```

### Configurer/modifier les codes
```bash
python setup_access_codes.py
```

### Lancer les tests backend
```bash
python -m pytest backend/
```

---

## 📱 Flux Utilisateur

```
┌──────────────────────────────────────────┐
│   Accueil - Page de Connexion            │
└──────────────────────────────────────────┘
                    ↓
        [Patient]  ou  [Personnel Santé]
                    ↓
        Personnel Santé sélectionné
                    ↓
┌──────────────────────────────────────────┐
│   Saisissez votre code d'accès           │
│   [_ _ _ _ _ _]                          │
│                                          │
│   [Se connecter]  [Changer de profil]    │
└──────────────────────────────────────────┘
                    ↓
        Code validé côté backend
                    ↓
        JWT token généré & sauvegardé
                    ↓
┌──────────────────────────────────────────┐
│   Dashboard Médical                      │
│   ✅ Patients                            │
│   ✅ Rendez-vous                         │
│   ✅ Dossiers                            │
│   ✅ Planning                            │
└──────────────────────────────────────────┘
```

---

## 🎯 Points Clés du Système

### Sécurité
- ✅ Code d'accès unique par personnel
- ✅ Validation côté backend
- ✅ JWT token généré après succès
- ✅ HTTPS obligatoire en production

### Avantages
- ✅ Accès rapide sans email/mot de passe
- ✅ Facile à gérer et à renouveler
- ✅ Contrôle centralisé des accès
- ✅ Audit trail possible

### Limites
- ⚠️ Code d'accès partagé = accès immédiat
- ⚠️ Renouvellement manuel nécessaire
- ⚠️ Pas de 2FA natif

---

## 📞 Troubleshooting

### "Code d'accès invalide"

**Cause probable:** Code incorrect ou non configuré

**Solution:**
```bash
python show_access_codes.py  # Vérifier les codes
python setup_access_codes.py  # Reconfigurer si nécessaire
```

### "Impossible de se connecter"

**Vérifier:**
1. Backend en cours d'exécution
   ```bash
   python backend/app.py
   ```

2. MySQL accessible
   ```bash
   mysql -u root gestion_des-rendez-vous5
   ```

3. Code d'accès dans la base
   ```sql
   SELECT id_personnel, nom, access_code FROM personnel_de_sante;
   ```

### "Code accepte plusieurs variations"

**Cause:** Fonction `normalize_access_code()` normalise le code

**Exemples acceptés:**
- `DOCD582EF0B` ✅
- `  DOCD582EF0B  ` ✅ (espaces)
- `docd582ef0b` ✅ (minuscules)
- `D ocd582 ef0b` ✅ (espaces internes)

---

## 📚 Documentation Complète

Pour plus d'informations:
- 📖 [ACCESS_CODE_SYSTEM.md](./ACCESS_CODE_SYSTEM.md) - Documentation technique complète
- 📖 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Endpoints API
- 📖 [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture système
- 📖 [QUICK_START.md](./QUICK_START.md) - Guide de démarrage complet

---

## ✨ Résumé

✅ Système opérationnel et testé  
✅ 4 personnels médicaux avec codes d'accès  
✅ Interface frontend intégrée  
✅ Backend prêt pour la production  

**Prochaines étapes:**
1. Générer des codes pour les nouveaux personnels si nécessaire
2. Tester l'accès via l'interface
3. Configurer HTTPS en production
4. Mettre en place un système de renouvellement des codes

---

**Dernière mise à jour:** 3 mai 2026  
**Version:** 1.0 - Production

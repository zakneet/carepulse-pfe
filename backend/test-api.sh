#!/bin/bash
# Script de tests d'intégration pour CarePulse

echo "========================================"
echo "TESTS D'INTÉGRATION - CarePulse"
echo "========================================"

BASE_URL="http://127.0.0.1:5000"

# ==========================================
# 1. TEST CONNECTION
# ==========================================
echo ""
echo "1. Test de connexion à la base de données..."
curl -s "$BASE_URL/test_connection" | jq .

# ==========================================
# 2. TEST REGISTER PATIENT
# ==========================================
echo ""
echo "2. Créer un compte testeur patient..."
curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Testeur",
    "prenom": "Patient",
    "email": "patient.test@example.com",
    "password": "password123",
    "telephone": "0123456789",
    "role": 1
  }' | jq .

# ==========================================
# 3. TEST LOGIN PATIENT
# ==========================================
echo ""
echo "3. Login patient (sans code d'accès)..."
PATIENT_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient.test@example.com",
    "password": "password123",
    "userType": "patient"
  }')

echo "$PATIENT_LOGIN_RESPONSE" | jq .

# Extraire le token
PATIENT_TOKEN=$(echo "$PATIENT_LOGIN_RESPONSE" | jq -r '.token // "error"')
echo "Token patient obtenu: ${PATIENT_TOKEN:0:20}..."

# ==========================================
# 4. TEST LOGIN MEDICAL STAFF - SANS CODE
# ==========================================
echo ""
echo "4. Test login médecin SANS code d'accès (doit échouer)..."
curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient.test@example.com",
    "password": "password123",
    "userType": "doctor"
  }' | jq .

# ==========================================
# 5. CRÉER UN CODE D'ACCÈS
# ==========================================
echo ""
echo "5. Admin: Créer un code d'accès pour médecins..."
curl -s -X POST "$BASE_URL/admin/access-codes" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "DOCTOR2024SECRET",
    "user_type": "doctor",
    "description": "Code de test pour médecins"
  }' | jq .

# ==========================================
# 6. TEST LOGIN MEDICAL STAFF - AVEC CODE
# ==========================================
echo ""
echo "6. Test login médecin AVEC code d'accès (doit réussir)..."
DOCTOR_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient.test@example.com",
    "password": "password123",
    "userType": "doctor",
    "accessCode": "DOCTOR2024SECRET"
  }')

echo "$DOCTOR_LOGIN_RESPONSE" | jq .

# Extraire le token médecin
DOCTOR_TOKEN=$(echo "$DOCTOR_LOGIN_RESPONSE" | jq -r '.token // "error"')
echo "Token médecin obtenu: ${DOCTOR_TOKEN:0:20}..."

# ==========================================
# 7. TEST GET_RDVS AVEC TOKEN
# ==========================================
echo ""
echo "7. Récupérer les RDVs (avec token patient)..."
if [ "$PATIENT_TOKEN" != "error" ]; then
  curl -s -X GET "$BASE_URL/get_rdvs" \
    -H "Authorization: Bearer $PATIENT_TOKEN" | jq .
else
  echo "Pas de token, test impossible"
fi

echo ""
echo "========================================"
echo "TESTS TERMINÉS"
echo "========================================"

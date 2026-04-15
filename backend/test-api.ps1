# Script de tests d'intégration pour CarePulse (PowerShell)

$baseUrl = "http://127.0.0.1:5000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTS D'INTÉGRATION - CarePulse" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ==========================================
# 1. TEST CONNECTION
# ==========================================
Write-Host "`n1. Test de connexion à la base de données..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/test_connection" -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

# ==========================================
# 2. TEST REGISTER PATIENT
# ==========================================
Write-Host "`n2. Créer un compte testeur patient..." -ForegroundColor Yellow
try {
    $registerData = @{
        nom = "Testeur"
        prenom = "Patient"
        email = "patient.test@example.com"
        password = "password123"
        telephone = "0123456789"
        role = 1
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerData `
        -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "Info: $_" -ForegroundColor Yellow
}

# ==========================================
# 3. TEST LOGIN PATIENT
# ==========================================
Write-Host "`n3. Login patient (sans code d'accès)..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = "patient.test@example.com"
        password = "password123"
        userType = "patient"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginData `
        -UseBasicParsing
    
    $result = $response.Content | ConvertFrom-Json
    Write-Host ($result | ConvertTo-Json)
    
    $script:patientToken = $result.token
    Write-Host "✓ Token patient obtenu: $($script:patientToken.Substring(0, 20))..." -ForegroundColor Green
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

# ==========================================
# 4. TEST LOGIN MEDICAL STAFF - SANS CODE
# ==========================================
Write-Host "`n4. Test login médecin SANS code d'accès (doit échouer)..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = "patient.test@example.com"
        password = "password123"
        userType = "doctor"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginData `
        -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "✓ Erreur attendue: Code d'accès requis" -ForegroundColor Green
    Write-Host $_.Exception.Response.StatusCode -ForegroundColor Green
}

# ==========================================
# 5. CRÉER UN CODE D'ACCÈS
# ==========================================
Write-Host "`n5. Admin: Créer un code d'accès pour médecins..." -ForegroundColor Yellow
try {
    $codeData = @{
        code = "DOCTOR2024SECRET"
        user_type = "doctor"
        description = "Code de test pour médecins"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/admin/access-codes" `
        -Method POST `
        -ContentType "application/json" `
        -Body $codeData `
        -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "Info: $_" -ForegroundColor Yellow
}

# ==========================================
# 6. TEST LOGIN MEDICAL STAFF - AVEC CODE
# ==========================================
Write-Host "`n6. Test login médecin AVEC code d'accès (doit réussir)..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = "patient.test@example.com"
        password = "password123"
        userType = "doctor"
        accessCode = "DOCTOR2024SECRET"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginData `
        -UseBasicParsing
    
    $result = $response.Content | ConvertFrom-Json
    Write-Host ($result | ConvertTo-Json)
    
    $script:doctorToken = $result.token
    Write-Host "✓ Token médecin obtenu: $($script:doctorToken.Substring(0, 20))..." -ForegroundColor Green
    Write-Host "Rôle: $($result.user.role)" -ForegroundColor Green
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}

# ==========================================
# 7. TEST GET_RDVS AVEC TOKEN PATIENT
# ==========================================
Write-Host "`n7. Récupérer les RDVs (avec token patient)..." -ForegroundColor Yellow
if ($script:patientToken) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/get_rdvs" `
            -Method GET `
            -Headers @{"Authorization" = "Bearer $($script:patientToken)"} `
            -UseBasicParsing
        $response.Content | ConvertFrom-Json | ConvertTo-Json
    } catch {
        Write-Host "Info: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTS TERMINÉS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

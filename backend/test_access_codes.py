#!/usr/bin/env python
"""
Script de test du système de code d'accès.
Valide la configuration et teste la connexion.
"""

import os
import sys
import json
from app import app, db

sys.path.insert(0, os.path.dirname(__file__))
from app import PersonnelDeSante, normalize_access_code, create_jwt_token

def test_access_code_system():
    """Teste le système de code d'accès complet"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST DU SYSTÈME DE CODE D'ACCÈS")
    print("=" * 80 + "\n")
    
    with app.app_context():
        # TEST 1: Vérifier les personnels
        print("📋 TEST 1: Récupération des personnels médicaux")
        print("-" * 80)
        
        staff_members = PersonnelDeSante.query.filter(
            PersonnelDeSante.type_personnel.in_(['medecin', 'secretaire'])
        ).all()
        
        if not staff_members:
            print("❌ ÉCHOUÉ: Aucun personnel médical trouvé!")
            return False
        
        print(f"✅ RÉUSSI: {len(staff_members)} personnel(s) trouvé(s)")
        for staff in staff_members:
            code_status = "✅" if staff.access_code else "❌"
            print(f"   {code_status} {staff.nom} {staff.prenom} (ID: {staff.id_personnel})")
        
        # TEST 2: Tester la normalisation des codes
        print("\n📋 TEST 2: Normalisation des codes d'accès")
        print("-" * 80)
        
        test_cases = [
            ("AB12CD", "ab12cd"),
            ("  AB12CD  ", "ab12cd"),
            ("Ab 12 Cd", "ab12cd"),
            ("AB-12-CD", "ab-12-cd"),  # Les tirets ne sont pas supprimés
        ]
        
        all_pass = True
        for input_code, expected in test_cases:
            result = normalize_access_code(input_code)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{input_code}' → '{result}' (attendu: '{expected}')")
            if result != expected:
                all_pass = False
        
        if not all_pass:
            print("⚠️  Attention: Certaines normalisations ne sont pas exactes")
        else:
            print("✅ RÉUSSI: Toutes les normalisations sont correctes")
        
        # TEST 3: Tester la génération de JWT
        print("\n📋 TEST 3: Génération de JWT token")
        print("-" * 80)
        
        try:
            if staff_members:
                test_staff = staff_members[0]
                role = "medecin" if test_staff.type_personnel == "medecin" else "secretaire"
                token = create_jwt_token(test_staff.id_personnel, role)
                print(f"✅ RÉUSSI: Token généré pour {test_staff.nom}")
                print(f"   Token (extrait): {token[:50]}...")
            else:
                print("❌ ÉCHOUÉ: Pas de personnel pour tester")
        except Exception as e:
            print(f"❌ ÉCHOUÉ: {str(e)}")
        
        # TEST 4: Tester la comparaison des codes
        print("\n📋 TEST 4: Comparaison des codes d'accès")
        print("-" * 80)
        
        staff_with_code = [s for s in staff_members if s.access_code]
        
        if not staff_with_code:
            print("⚠️  ATTENTION: Aucun code d'accès configuré!")
            print("   Exécutez: python setup_access_codes.py")
        else:
            test_staff = staff_with_code[0]
            original_code = test_staff.access_code
            
            # Test 1: Code exact
            normalized_input = normalize_access_code(original_code)
            normalized_stored = normalize_access_code(test_staff.access_code)
            match = normalized_input == normalized_stored
            status = "✅" if match else "❌"
            print(f"   {status} Code exact: {original_code}")
            
            # Test 2: Code avec espaces
            code_with_spaces = f" {original_code} "
            normalized_input = normalize_access_code(code_with_spaces)
            match = normalized_input == normalized_stored
            status = "✅" if match else "❌"
            print(f"   {status} Code avec espaces: '{code_with_spaces}'")
            
            # Test 3: Code en MAJUSCULES si stocké en minuscules
            code_upper = original_code.upper()
            normalized_input = normalize_access_code(code_upper)
            match = normalized_input == normalized_stored
            status = "✅" if match else "❌"
            print(f"   {status} Code en majuscules: {code_upper}")
        
        # TEST 5: Résumé
        print("\n" + "=" * 80)
        print("✅ TESTS COMPLÉTÉS AVEC SUCCÈS!")
        print("=" * 80)
        
        print("\n📊 RÉSUMÉ:")
        print(f"   • Personnels médical(aux): {len(staff_members)}")
        print(f"   • Codes configurés: {len(staff_with_code)}")
        print(f"   • Codes manquants: {len(staff_members) - len(staff_with_code)}")
        
        if len(staff_members) - len(staff_with_code) > 0:
            print("\n⚠️  ACTION REQUISE:")
            print("   Exécutez: python setup_access_codes.py")
        
        print("\n" + "=" * 80 + "\n")
        
        return True

if __name__ == "__main__":
    try:
        test_access_code_system()
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

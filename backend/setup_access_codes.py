#!/usr/bin/env python
"""
Script de configuration des codes d'accès pour le personnel médical (Médecins et Nurses).
Les codes d'accès sont générés ou vous pouvez les définir manuellement.
"""

import os
import sys
import string
import random
from app import app, db

# Importer les modèles
sys.path.insert(0, os.path.dirname(__file__))
from app import PersonnelDeSante

def generate_access_code(length=6):
    """Génère un code d'accès aléatoire alphanumérique"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def setup_access_codes():
    """Configure les codes d'accès pour tous les personnels médicaux"""
    
    with app.app_context():
        # Récupérer tous les personnels médicaux
        staff_members = PersonnelDeSante.query.all()
        
        if not staff_members:
            print("❌ Aucun personnel médical trouvé dans la base de données.")
            return
        
        print(f"\n📋 Configuration des codes d'accès pour {len(staff_members)} personnel(s) médical(aux)\n")
        print("-" * 80)
        
        codes_config = {}
        
        for staff in staff_members:
            print(f"\n👤 {staff.nom.upper()} {staff.prenom}")
            print(f"   ID: {staff.id_personnel}")
            print(f"   Specialite: {staff.specialite}")
            
            if staff.access_code:
                print(f"   ✅ Code existant: {staff.access_code}")
                action = input("   Garder ce code ou en générer un nouveau ? (G=Garder/N=Nouveau) [G]: ").strip().upper() or "G"
                
                if action == "G":
                    codes_config[staff.id_personnel] = staff.access_code
                    continue
            
            # Générer un nouveau code
            new_code = generate_access_code(6)
            print(f"   🔑 Code généré: {new_code}")
            
            # Demander confirmation
            confirm = input("   Confirmer ce code ? (O/N) [O]: ").strip().upper() or "O"
            
            if confirm == "O":
                staff.access_code = new_code
                codes_config[staff.id_personnel] = new_code
            else:
                # Permettre à l'utilisateur de saisir un code personnalisé
                custom_code = input("   Saisir un code personnalisé (ou vide pour ignorer): ").strip().upper()
                if custom_code:
                    staff.access_code = custom_code
                    codes_config[staff.id_personnel] = custom_code
                else:
                    print("   ⏭️  Ignoré")
        
        # Sauvegarder les modifications
        if codes_config:
            try:
                db.session.commit()
                print("\n" + "=" * 80)
                print("✅ CODES D'ACCÈS CONFIGURÉS AVEC SUCCÈS!\n")
                print("📝 Résumé des codes d'accès:\n")
                
                for staff in staff_members:
                    if staff.id_personnel in codes_config:
                        print(f"  • {staff.nom} {staff.prenom}: {codes_config[staff.id_personnel]}")
                
                print("\n" + "=" * 80)
                print("🔒 SÉCURITÉ:")
                print("   - Les codes doivent être conservés de manière sécurisée")
                print("   - Les codes d'accès remplacent la saisie d'email/mot de passe")
                print("   - Un code = accès immédiat à l'interface médicale")
                print("=" * 80)
                
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Erreur lors de la sauvegarde: {str(e)}")
        else:
            print("\n⚠️  Aucun code d'accès n'a été configuré.")

if __name__ == "__main__":
    setup_access_codes()

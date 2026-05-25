#!/usr/bin/env python
"""
Script simple pour afficher les codes d'accès actuels du personnel médical.
"""

import os
import sys
from app import app, db

sys.path.insert(0, os.path.dirname(__file__))
from app import PersonnelDeSante

def show_access_codes():
    """Affiche les codes d'accès configurés"""
    
    with app.app_context():
        staff_members = PersonnelDeSante.query.filter(
            PersonnelDeSante.type_personnel.in_(['medecin', 'secretaire'])
        ).all()
        
        if not staff_members:
            print("❌ Aucun personnel médical trouvé.")
            return
        
        print("\n" + "=" * 80)
        print("🔐 CODES D'ACCÈS - PERSONNEL MÉDICAL")
        print("=" * 80 + "\n")
        
        has_codes = False
        for staff in staff_members:
            status = "✅" if staff.access_code else "❌"
            code_display = staff.access_code if staff.access_code else "Non configuré"
            
            if staff.access_code:
                has_codes = True
            
            print(f"{status} {staff.nom.upper()} {staff.prenom}")
            print(f"   ID: {staff.id_personnel}")
            print(f"   Type: {staff.type_personnel.capitalize()}")
            print(f"   Code: {code_display}")
            print(f"   Email: {staff.email}\n")
        
        if not has_codes:
            print("\n⚠️  ATTENTION: Aucun code d'accès n'a été configuré!")
            print("   Exécutez: python setup_access_codes.py")
        
        print("=" * 80)

if __name__ == "__main__":
    show_access_codes()

#!/usr/bin/env python
"""
Script de test du système de code d'accès (version simplifiée).
"""

import os
import sys
import pymysql
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "gestion_des-rendez-vous5")

def test_access_code_system():
    """Teste le système de code d'accès en base de données"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST DU SYSTÈME DE CODE D'ACCÈS")
    print("=" * 80 + "\n")
    
    try:
        # Connexion à la base de données
        print("📋 TEST 1: Connexion à la base de données")
        print("-" * 80)
        
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        
        print("✅ RÉUSSI: Connexion établie")
        print(f"   Host: {MYSQL_HOST}:{MYSQL_PORT}")
        print(f"   Database: {MYSQL_DB}")
        
        # TEST 2: Vérifier les personnels
        print("\n📋 TEST 2: Récupération des personnels médicaux")
        print("-" * 80)
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        query = """
            SELECT id_personnel, nom, prenom, email, type_personnel, access_code
            FROM personnel_de_sante
            WHERE type_personnel IN ('medecin', 'secretaire')
        """
        
        cursor.execute(query)
        staff_members = cursor.fetchall()
        
        if not staff_members:
            print("❌ ÉCHOUÉ: Aucun personnel médical trouvé!")
            cursor.close()
            connection.close()
            return False
        
        print(f"✅ RÉUSSI: {len(staff_members)} personnel(s) trouvé(s)\n")
        
        staff_with_code = 0
        for staff in staff_members:
            code_status = "✅" if staff['access_code'] else "❌"
            code_display = staff['access_code'] if staff['access_code'] else "Non configuré"
            
            if staff['access_code']:
                staff_with_code += 1
            
            print(f"   {code_status} {staff['nom'].upper()} {staff['prenom']}")
            print(f"      ID: {staff['id_personnel']}")
            print(f"      Type: {staff['type_personnel']}")
            print(f"      Code: {code_display}\n")
        
        # TEST 3: Vérifier la structure de la table
        print("📋 TEST 3: Vérification de la structure de la table")
        print("-" * 80)
        
        query_schema = """
            SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'personnel_de_sante'
            AND COLUMN_NAME IN ('access_code', 'type_personnel')
        """
        
        cursor.execute(query_schema, (MYSQL_DB,))
        columns = cursor.fetchall()
        
        if columns:
            print("✅ RÉUSSI: Colonnes vérifiées\n")
            for col in columns:
                unique = "(UNIQUE)" if col['COLUMN_KEY'] == 'UNI' else ""
                nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
                print(f"   • {col['COLUMN_NAME']}: {col['COLUMN_TYPE']} {nullable} {unique}")
        else:
            print("❌ ÉCHOUÉ: Colonnes non trouvées!")
        
        # TEST 4: Résumé
        print("\n" + "=" * 80)
        print("✅ TESTS COMPLÉTÉS AVEC SUCCÈS!")
        print("=" * 80)
        
        print("\n📊 RÉSUMÉ:")
        print(f"   • Personnels médical(aux): {len(staff_members)}")
        print(f"   • Codes configurés: {staff_with_code}")
        print(f"   • Codes manquants: {len(staff_members) - staff_with_code}")
        
        if len(staff_members) - staff_with_code > 0:
            print("\n⚠️  ACTION REQUISE:")
            print("   Exécutez: python setup_access_codes.py")
        
        print("\n" + "=" * 80 + "\n")
        
        cursor.close()
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ ERREUR Base de Données: {str(e)}")
        print("\nVérifiez:")
        print("   • MySQL est en cours d'exécution")
        print("   • Les identifiants sont corrects")
        print("   • La base de données existe")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_access_code_system()
    sys.exit(0 if success else 1)

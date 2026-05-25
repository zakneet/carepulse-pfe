#!/usr/bin/env python3
"""Test direct SQLAlchemy connection to verify DB is accessible from Flask context."""

import sys
sys.path.insert(0, '.')

import app as app_module
app = app_module.app
db = app_module.db

print("[INFO] Testing SQLAlchemy connection from Flask app...")

with app.app_context():
    try:
        # Test basic connection
        result = db.session.execute(db.text("SELECT 1"))
        print("[OK] Direct SQL query: SELECT 1 works")
        
        # Test table access
        result = db.session.execute(db.text("SELECT COUNT(*) FROM personnel_de_sante"))
        count = result.scalar()
        print(f"[OK] Raw SQL: Found {count} personnel records")
        
        # Try to fetch personnel data
        result = db.session.execute(db.text("SELECT id_personnel, nom, prenom FROM personnel_de_sante WHERE id_personnel = 1 LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"[OK] Personnel #1 found: {row[0]} - {row[1]} {row[2]}")
        else:
            print("[WARN] Personnel #1 not found in DB")
            
            # Check what we have
            result = db.session.execute(db.text("SELECT id_personnel FROM personnel_de_sante"))
            ids = [r[0] for r in result.fetchall()]
            print(f"[INFO] Available personnel IDs: {ids}")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

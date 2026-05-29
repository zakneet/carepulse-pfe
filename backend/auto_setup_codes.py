import os
import string
import random
from app import app, db, PersonnelDeSante, _ensure_personnel_table_columns

def generate_access_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

with app.app_context():
    _ensure_personnel_table_columns()
    
    staff_members = PersonnelDeSante.query.all()
    count = 0
    for staff in staff_members:
        if not staff.access_code:
            staff.access_code = generate_access_code()
            count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Generated new access codes for {count} doctors.")
    else:
        print("All doctors already have access codes.")

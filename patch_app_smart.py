import re

with open('backend/app.py', 'r', encoding='utf-8') as f:
    app_py_code = f.read()

new_endpoints = """
# ==============================================================================
# SMART SCHEDULING (OR-TOOLS) ENDPOINTS
# ==============================================================================

try:
    from services.smart_scheduling import SmartSchedulingService
except ImportError:
    pass # Wait, let's just make sure it's imported at the top or here.
    
@app.route("/appointments/smart-booking", methods=["POST"])
def smart_booking():
    from services.smart_scheduling import SmartSchedulingService
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    doctor_id = data.get("idPersonnel")
    date_str = data.get("date")
    rejected_slots = data.get("rejectedSlots", [])
    
    if not doctor_id or not date_str:
        return jsonify({"error": "idPersonnel and date are required"}), 400
        
    try:
        result = SmartSchedulingService.suggest_optimal_slot(db, Planning, Rdv, doctor_id, date_str, duration=30, rejected_slots=rejected_slots)
        if not result:
            return jsonify({"error": "Aucun créneau disponible pour cette date"}), 404
            
        # Get doctor details for the frontend
        doc = PersonnelDeSante.query.get(doctor_id)
        if doc:
            result['doctor'] = {
                'nom': doc.nom,
                'prenom': doc.prenom,
                'specialite': doc.specialite
            }
        else:
            result['doctor'] = {'nom': '', 'prenom': '', 'specialite': ''}
            
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/appointments/alternative-slot", methods=["POST"])
def alternative_slot():
    # Same logic but expected to have rejectedSlots populated
    from services.smart_scheduling import SmartSchedulingService
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    doctor_id = data.get("idPersonnel")
    date_str = data.get("date")
    rejected_slots = data.get("rejectedSlots", [])
    
    if not doctor_id or not date_str:
        return jsonify({"error": "idPersonnel and date are required"}), 400
        
    try:
        result = SmartSchedulingService.suggest_optimal_slot(db, Planning, Rdv, doctor_id, date_str, duration=30, rejected_slots=rejected_slots)
        if not result:
            return jsonify({"error": "Aucune alternative disponible"}), 404
            
        doc = PersonnelDeSante.query.get(doctor_id)
        if doc:
            result['doctor'] = {
                'nom': doc.nom,
                'prenom': doc.prenom,
                'specialite': doc.specialite
            }
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""

# Insert right before the if __name__ block
if 'if __name__ == "__main__":' in app_py_code:
    app_py_code = app_py_code.replace('if __name__ == "__main__":', new_endpoints + '\nif __name__ == "__main__":')
else:
    app_py_code += new_endpoints

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(app_py_code)

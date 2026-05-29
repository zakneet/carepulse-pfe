from .optimization_service import ORToolsSolver
from .scoring_engine import SlotScoringEngine
from datetime import datetime, date, time, timedelta

class SmartSchedulingService:
    @staticmethod
    def suggest_optimal_slot(db, planning_model, rdv_model, doctor_id, date_str, duration=30, rejected_slots=None):
        """
        Fetches DB constraints, calls OR-Tools, scores the result.
        Returns dict with optimal slot, doctor info, score, explanation.
        """
        try:
            doctor_id = int(doctor_id)
        except (TypeError, ValueError):
            return None

        if isinstance(date_str, date):
            target_date = date_str
        else:
            try:
                target_date = datetime.fromisoformat(str(date_str)).date()
            except (TypeError, ValueError):
                try:
                    target_date = datetime.strptime(str(date_str), "%Y-%m-%d").date()
                except (TypeError, ValueError):
                    return None

        # Fetch planning windows
        plannings = planning_model.query.filter_by(idPersonnel=doctor_id, date=target_date).all()
        
        # If no planning is found, default to 08:00 - 18:00
        windows = []
        if plannings:
            for p in plannings:
                # Assuming heure_debut and heure_fin are strings 'HH:MM' or timedelta
                start = SmartSchedulingService._to_minutes(p.heure_debut)
                end = SmartSchedulingService._to_minutes(p.heure_fin)
                windows.append({'start': start, 'end': end})
        else:
            windows = [{'start': 8 * 60, 'end': 18 * 60}]
            
        # Fetch existing appointments
        appointments_db = rdv_model.query.filter_by(idPersonnel=doctor_id, dateRDV=target_date).all()
        appointments = []
        for a in appointments_db:
            if a.heureDebut and a.heureFin:
                appointments.append({
                    'start': SmartSchedulingService._to_minutes(a.heureDebut),
                    'end': SmartSchedulingService._to_minutes(a.heureFin)
                })
                
        # Call OR-Tools solver
        optimal_slot = ORToolsSolver.find_optimal_slot(windows, appointments, duration, rejected_slots)
        
        if not optimal_slot:
            return None
            
        # Score the slot
        scoring = SlotScoringEngine.calculate_score(optimal_slot, windows, appointments)
        
        return {
            'slot': optimal_slot,
            'score': scoring['score'],
            'explanation': scoring['explanation']
        }

    @staticmethod
    def _to_minutes(time_val):
        if not time_val:
            return 0
        if isinstance(time_val, datetime):
            time_val = time_val.time()
        if isinstance(time_val, time):
            return (time_val.hour * 60) + time_val.minute
        if isinstance(time_val, timedelta):
            return int(time_val.total_seconds() // 60)
        if hasattr(time_val, 'components'):  # pandas timedelta
            return time_val.components.hours * 60 + time_val.components.minutes
        if hasattr(time_val, 'seconds'):  # datetime.timedelta-like
            return int(time_val.seconds // 60)
        if isinstance(time_val, str):
            parts = time_val.split(':')
            if len(parts) >= 2:
                return int(parts[0]) * 60 + int(parts[1])
        return 0

    @staticmethod
    def reoptimize_day_schedule(db, planning_model, rdv_model, doctor_id, date_str, emergency_duration=None, cancelled_id=None):
        try:
            doctor_id = int(doctor_id)
        except (TypeError, ValueError):
            return None

        if isinstance(date_str, date):
            target_date = date_str
        else:
            try:
                target_date = datetime.fromisoformat(str(date_str)).date()
            except (TypeError, ValueError):
                try:
                    target_date = datetime.strptime(str(date_str), "%Y-%m-%d").date()
                except (TypeError, ValueError):
                    return None

        # Fetch planning windows
        plannings = planning_model.query.filter_by(idPersonnel=doctor_id, date=target_date).all()
        windows = []
        if plannings:
            for p in plannings:
                start = SmartSchedulingService._to_minutes(p.heure_debut)
                end = SmartSchedulingService._to_minutes(p.heure_fin)
                windows.append({'start': start, 'end': end})
        else:
            windows = [{'start': 8 * 60, 'end': 18 * 60}]
            
        # Fetch existing appointments
        appointments_db = rdv_model.query.filter_by(idPersonnel=doctor_id, dateRDV=target_date).all()
        appointments = []
        for a in appointments_db:
            if cancelled_id and a.idRdv == cancelled_id:
                continue
            if a.heureDebut and a.heureFin:
                s = SmartSchedulingService._to_minutes(a.heureDebut)
                e = SmartSchedulingService._to_minutes(a.heureFin)
                appointments.append({
                    'id': a.idRdv,
                    'start': s,
                    'duration': max(15, e - s) # Default minimum duration 15m
                })
                
        # Run optimization
        result = ORToolsSolver.reoptimize_schedule(windows, appointments, emergency_duration)
        if not result:
            return None
            
        # Format output
        moves_info = []
        for appt_id, new_start in result.get('moves', {}).items():
            appt = next((a for a in appointments_db if a.idRdv == appt_id), None)
            if not appt: continue
            
            old_start_str = str(appt.heureDebut)[:5]
            old_end_str = str(appt.heureFin)[:5]
            
            dur = next(a['duration'] for a in appointments if a['id'] == appt_id)
            new_h = new_start // 60
            new_m = new_start % 60
            new_e_m = (new_start + dur) % 60
            new_e_h = (new_start + dur) // 60
            
            new_start_str = f"{new_h:02d}:{new_m:02d}:00"
            new_end_str = f"{new_e_h:02d}:{new_e_m:02d}:00"
            
            moves_info.append({
                'id': appt_id,
                'oldStart': old_start_str,
                'oldEnd': old_end_str,
                'newStart': new_start_str,
                'newEnd': new_end_str
            })
            
        final_result = {'moves': moves_info}
        if 'emergency' in result:
            e_s = result['emergency']
            e_e = e_s + emergency_duration
            final_result['emergency_slot'] = {
                'start': f"{e_s//60:02d}:{e_s%60:02d}:00",
                'end': f"{e_e//60:02d}:{e_e%60:02d}:00"
            }
            
        return final_result

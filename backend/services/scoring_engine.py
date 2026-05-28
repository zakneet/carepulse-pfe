class SlotScoringEngine:
    @staticmethod
    def calculate_score(slot, planning_windows, appointments):
        """
        Evaluates how good a slot is.
        Score out of 100%.
        Criteria:
        - Gap filling: Does it perfectly fill a gap between appointments? (+20)
        - Continuity: Is it directly adjacent to an existing appointment or start/end of planning window? (+50)
        - Dead time: Does it avoid creating small <30m dead gaps? (+30)
        """
        score = 80  # Base high score for being a valid slot
        explanation = "Ce créneau est disponible et respecte vos contraintes."
        
        # Check continuity
        is_adjacent = False
        creates_small_gap = False
        
        start_min = slot['start']
        end_min = slot['end']
        
        # Distance to nearest bounds
        min_dist = 9999
        
        # Check against windows
        for w in planning_windows:
            if start_min == w['start'] or end_min == w['end']:
                is_adjacent = True
            
            # Check gap size to window bounds
            dist_to_start = start_min - w['start']
            dist_to_end = w['end'] - end_min
            
            if dist_to_start >= 0 and dist_to_start < min_dist:
                min_dist = dist_to_start
            if dist_to_end >= 0 and dist_to_end < min_dist:
                min_dist = dist_to_end
        
        # Check against appointments
        for appt in appointments:
            if start_min == appt['end'] or end_min == appt['start']:
                is_adjacent = True
                
            # Check gap size to appointments
            dist_to_appt_end = start_min - appt['end']
            dist_to_appt_start = appt['start'] - end_min
            
            if dist_to_appt_end >= 0 and dist_to_appt_end < min_dist:
                min_dist = dist_to_appt_end
            if dist_to_appt_start >= 0 and dist_to_appt_start < min_dist:
                min_dist = dist_to_appt_start
                
        if is_adjacent:
            score += 15
            explanation = "Ce créneau optimise le planning en s'accolant à un autre rendez-vous (minimise les temps morts)."
            
        if min_dist > 0 and min_dist < 30:
            score -= 20
            explanation = "Créneau alternatif trouvé, mais il laisse un léger temps mort dans l'emploi du temps."
            
        if score > 98:
            score = 98  # Cap
            
        return {
            'score': f"{score}%",
            'explanation': explanation
        }

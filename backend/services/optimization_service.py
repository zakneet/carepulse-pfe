from ortools.sat.python import cp_model

class ORToolsSolver:
    @staticmethod
    def find_optimal_slot(planning_windows, appointments, duration_minutes, rejected_slots=None):
        """
        planning_windows: list of dicts {'start': min, 'end': min} (e.g. 9*60 to 17*60)
        appointments: list of dicts {'start': min, 'end': min}
        duration_minutes: int
        rejected_slots: list of dicts {'start': min}
        """
        if not rejected_slots:
            rejected_slots = []
            
        model = cp_model.CpModel()
        
        # We need a start variable
        min_time = min(w['start'] for w in planning_windows) if planning_windows else 8 * 60
        max_time = max(w['end'] for w in planning_windows) if planning_windows else 18 * 60
        
        start_var = model.NewIntVar(min_time, max_time - duration_minutes, 'start_var')
        end_var = model.NewIntVar(min_time + duration_minutes, max_time, 'end_var')
        
        model.Add(end_var == start_var + duration_minutes)
        
        # Constraint: Must be within one of the planning windows
        # To do this, we create boolean variables for each window
        window_bools = []
        for i, window in enumerate(planning_windows):
            b = model.NewBoolVar(f'in_window_{i}')
            window_bools.append(b)
            # if b is true, start >= window['start'] and end <= window['end']
            model.Add(start_var >= window['start']).OnlyEnforceIf(b)
            model.Add(end_var <= window['end']).OnlyEnforceIf(b)
            
        if window_bools:
            model.AddExactlyOne(window_bools)
            
        # Constraint: Must not overlap with existing appointments
        for i, appt in enumerate(appointments):
            # start_var >= appt['end'] OR end_var <= appt['start']
            b_after = model.NewBoolVar(f'after_appt_{i}')
            b_before = model.NewBoolVar(f'before_appt_{i}')
            
            model.Add(start_var >= appt['end']).OnlyEnforceIf(b_after)
            model.Add(end_var <= appt['start']).OnlyEnforceIf(b_before)
            
            model.AddBoolOr([b_after, b_before])
            
        # Constraint: Must not be one of the rejected slots
        for i, rej in enumerate(rejected_slots):
            # start_var != rej['start']
            b_diff_before = model.NewBoolVar(f'diff_before_{i}')
            b_diff_after = model.NewBoolVar(f'diff_after_{i}')
            
            model.Add(start_var < rej['start']).OnlyEnforceIf(b_diff_before)
            model.Add(start_var > rej['start']).OnlyEnforceIf(b_diff_after)
            
            model.AddBoolOr([b_diff_before, b_diff_after])

        # Objective: We want to pack it close to existing appointments or start of day to avoid fragmentation
        # We can minimize start_var as a simple heuristic for packing early
        model.Minimize(start_var)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {
                'start': solver.Value(start_var),
                'end': solver.Value(end_var)
            }
        
        return None

    @staticmethod
    def reoptimize_schedule(planning_windows, appointments, emergency_duration=None):
        """
        Re-packs appointments to remove gaps.
        If emergency_duration is provided, an emergency appointment is added and prioritized 
        to happen as early as possible.
        appointments: [{'id': 1, 'duration': 30, 'start': 480}, ...]
        Returns: {'emergency': start_min, 'moves': {id: new_start_min}}
        """
        model = cp_model.CpModel()
        
        min_time = min(w['start'] for w in planning_windows) if planning_windows else 8 * 60
        max_time = max(w['end'] for w in planning_windows) if planning_windows else 18 * 60

        appts_vars = {}
        intervals = []
        
        for appt in appointments:
            start_var = model.NewIntVar(min_time, max_time - appt['duration'], f"start_{appt['id']}")
            end_var = model.NewIntVar(min_time + appt['duration'], max_time, f"end_{appt['id']}")
            model.Add(end_var == start_var + appt['duration'])
            
            interval_var = model.NewIntervalVar(start_var, appt['duration'], end_var, f"interval_{appt['id']}")
            intervals.append(interval_var)
            
            appts_vars[appt['id']] = start_var
            
            # Must be in one of the windows
            window_bools = []
            for i, window in enumerate(planning_windows):
                b = model.NewBoolVar(f"in_win_{appt['id']}_{i}")
                window_bools.append(b)
                model.Add(start_var >= window['start']).OnlyEnforceIf(b)
                model.Add(end_var <= window['end']).OnlyEnforceIf(b)
            if window_bools:
                model.AddExactlyOne(window_bools)

        em_start = None
        if emergency_duration:
            em_start = model.NewIntVar(min_time, max_time - emergency_duration, "em_start")
            em_end = model.NewIntVar(min_time + emergency_duration, max_time, "em_end")
            model.Add(em_end == em_start + emergency_duration)
            em_interval = model.NewIntervalVar(em_start, emergency_duration, em_end, "em_interval")
            intervals.append(em_interval)
            
            window_bools = []
            for i, window in enumerate(planning_windows):
                b = model.NewBoolVar(f"em_in_win_{i}")
                window_bools.append(b)
                model.Add(em_start >= window['start']).OnlyEnforceIf(b)
                model.Add(em_end <= window['end']).OnlyEnforceIf(b)
            if window_bools:
                model.AddExactlyOne(window_bools)

        # No overlapping
        model.AddNoOverlap(intervals)

        # Objective: Pack as early as possible. 
        # Emergency (if exists) has a huge weight to be earliest.
        # Other appointments prefer their original time, or as early as possible.
        objective_terms = []
        for appt in appointments:
            # Shift penalty: (start_var - original_start)^2 or just absolute diff
            # To keep it linear, use absolute difference
            diff = model.NewIntVar(0, max_time, f"diff_{appt['id']}")
            model.Add(diff >= start_var - appt['start'])
            model.Add(diff >= appt['start'] - start_var)
            
            # Prefer keeping original time, but also pulling earlier if there are gaps (cancel)
            # We want to pull earlier if there is a gap.
            objective_terms.append(diff * 10)
            objective_terms.append(start_var * 1) # Slight pressure to pack early
            
        if em_start is not None:
            objective_terms.append(em_start * 1000) # Emergency MUST be earliest
            
        model.Minimize(sum(objective_terms))

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            moves = {}
            for aid, var in appts_vars.items():
                if solver.Value(var) != [a['start'] for a in appointments if a['id'] == aid][0]:
                    moves[aid] = solver.Value(var)
                    
            res = {'moves': moves}
            if em_start is not None:
                res['emergency'] = solver.Value(em_start)
            return res
            
        return None


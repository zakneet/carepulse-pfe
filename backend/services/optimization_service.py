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

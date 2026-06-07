import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

export interface OptimizePatient {
  id: number;
  patientDbId?: number;
  start: number;
  end: number;
  duration: number;
  priority?: number;
  isUrgent?: boolean;
  nom?: string;
  prenom?: string;
  telephone?: string;
  cin?: string;
  motif?: string;
}

export interface OptimizeDoctorSchedule {
  start: number;
  end: number;
}

export interface OptimizeRequest {
  patients: OptimizePatient[];
  doctor_schedule: OptimizeDoctorSchedule;
}

export interface OptimizedAppointment {
  patient_id: number;
  start: number;
  end: number;
}

export interface OptimizeResponse {
  status: 'success' | 'error';
  data: OptimizedAppointment[];
  message?: string;
}

export interface Rdv {
  id: number;
  idRdv?: number;
  idRDV?: number;
  idPatient?: number;
  idPersonnel?: number;
  personnelNom?: string;
  personnelPrenom?: string;
  dateRDV: string;
  heureDebut: string;
  heureFin?: string;
  motifConsultation: string;
  statut?: string;
}

export interface NewRdv {
  idPatient: number;
  idPersonnel: number;
  dateRDV: string;
  heureDebut: string;
  heureFin?: string;
  motifConsultation: string;
  statut?: string;
  isUrgent?: boolean;
  nom?: string;
  prenom?: string;
  telephone?: string;
  email?: string;
  agePatient?: number;
}

export interface MedicalStaff {
  id: number;
  nom: string;
  prenom: string;
  specialite?: string;
}

export interface SuggestedSlot {
  heureDebut: string;
  heureFin: string;
}

export interface SlotSuggestionRequest {
  idPersonnel: number;
  dateRDV: string;
  isUrgent: boolean;
  slotDuration?: number;
  proposalIndex?: number;
}

export interface SlotSuggestionResponse {
  dateRDV: string;
  idPersonnel: number;
  isUrgent: boolean;
  slotDuration: number;
  type?: 'urgent_optimized';
  urgentSlot?: {
    heureDebut: string;
    heureFin: string;
  };
  rescheduledAppointments?: Array<{
    id: number;
    old_start: number;
    new_start: number;
    new_end: number;
  }>;
  planningContext?: {
    weekStart: string;
    weekEnd: string;
    todayAppointments: number;
    weekAppointments: number;
    hasPlanning?: boolean;
    planningWindows?: number;
    planningSource?: 'planning' | 'default';
  };
  suggestedSlots: SuggestedSlot[];
  optimizedSuggestedSlots?: SuggestedSlot[];
}

export interface PatientTodayAccessResponse {
  access: boolean;
  doctor_status?: string;
  your_appointment_time?: string;
  message?: string;
  totalPatients?: number;
  patientsWaiting?: number;
  waitTime?: number;
}

export interface MedicalPlanningAppointment {
  id: number;
  idPatient?: number;
  idPersonnel?: number;
  dateRDV: string;
  heureDebut: string;
  heureFin?: string;
  motifConsultation?: string;
  statut?: string;
  patientNom?: string;
  patientPrenom?: string;
  patientEmail?: string;
  patientCin?: string;
  medecinNom?: string;
  medecinPrenom?: string;
  medecin?: string;
  specialite?: string;
}

export interface PatientHistoryAppointment {
  id: number;
  idPersonnel?: number | null;
  dateRDV: string;
  heureDebut: string;
  heureFin?: string;
  motifConsultation?: string;
  statut?: string;
  medecin?: string;
  medecinNom?: string;
  medecinPrenom?: string;
  specialite?: string;
}

export interface PatientDashboardAppointment extends PatientHistoryAppointment {
  medecin?: string;
  medecinNom?: string;
  medecinPrenom?: string;
  specialite?: string;
}

export interface PatientDashboardMedicalRecord {
  sexe?: string | null;
  dateNaissance?: string | null;
  historique?: string | null;
  allergies: string[];
  maladies: string[];
}

export interface PatientDashboardResponse {
  patient: {
    id: number;
    nom: string;
    prenom: string;
    nomComplet: string;
    email?: string | null;
    telephone?: string | null;
    cin?: string | null;
    adresse?: string | null;
  };
  dossierMedical: PatientDashboardMedicalRecord;
  historyCount: number;
  appointments: PatientDashboardAppointment[];
  lastAppointment?: PatientDashboardAppointment | null;
}

export interface MedicalStaffPatientProfile {
  id: number;
  nom: string;
  prenom: string;
  cin?: string | null;
  sexe?: string | null;
  telephone?: string | null;
  email?: string | null;
  statut?: number;
  statut_label?: string;
}

export interface MedicalStaffPatientFullProfile extends MedicalStaffPatientProfile {
  nomComplet: string;
  dateNaissance?: string | null;
  age?: number | null;
  allergies: string[];
  maladies: string[];
}

export interface MedicalStaffPatientRecordResponse {
  patient: MedicalStaffPatientProfile;
  currentDoctorId: number;
  historyCount: number;
  lastAppointment?: PatientHistoryAppointment | null;
  appointments: PatientHistoryAppointment[];
}

export interface MedicalStaffPatientFullProfileResponse {
  patient: MedicalStaffPatientFullProfile;
  currentDoctorId: number;
  historyCount: number;
  lastAppointment?: PatientHistoryAppointment | null;
  appointments: PatientHistoryAppointment[];
}

export interface MedicalStaffPatientCinSearchResponse {
  found: boolean;
  cin: string;
  patient?: MedicalStaffPatientProfile;
}

export interface MedicalStaffPatientSavePayload {
  idPersonnel: number;
  patient: {
    nom: string;
    prenom: string;
    cin?: string | null;
    telephone?: string | null;
    email?: string | null;
  };
}

export interface MedicalStaffPatientSaveResponse {
  message: string;
  created: boolean;
  patient: MedicalStaffPatientProfile;
}

export interface MedicalStaffPatientListItem {
  id: number;
  nom: string;
  prenom: string;
  email?: string | null;
  telephone?: string | null;
  rdvCount: number;
  lastVisit?: string | null;
  nextVisit?: string | null;
  condition?: string;
  risk?: 'LOW' | 'MODERATE' | 'HIGH';
  newThisMonth?: boolean;
}

export interface MedicalStaffPatientProfileUpdatePayload {
  idPersonnel: number;
  idPatient: number;
  patient: {
    nom?: string;
    prenom?: string;
    email?: string | null;
    telephone?: string | null;
    cin?: string | null;
    sexe?: string | null;
    dateNaissance?: string | null;
    allergies?: string[];
    maladies?: string[];
  };
}

export interface MedicalPlanningDay {
  date: string;
  count: number;
  appointments: MedicalPlanningAppointment[];
}

export interface MedicalStaffPlanningResponse {
  idPersonnel: number;
  date: string;
  weekStart: string;
  weekEnd: string;
  todayPlanning: MedicalPlanningAppointment[];
  weekPlanning: MedicalPlanningDay[];
  stats: {
    todayCount: number;
    weekCount: number;
  };
}

export interface OptimizePlanningResponse {
  message: string;
  updatedRows: Array<{
    id: number;
    heureDebut: string;
    heureFin: string;
    idPatient: number;
    idPersonnel: number;
    statut?: string;
  }>;
  optimizedPlan: Array<{
    patientId: number;
    heureDebut: string;
    heureFin: string;
  }>;
  planningContext?: {
    hasPlanning: boolean;
    planningSource: 'planning' | 'default';
    planningWindows: number;
  };
  updatedSchedule: MedicalPlanningAppointment[];
}

export interface ShortAbsenceRecalculationResponse {
  message: string;
  updatedRows: Array<{
    id: number;
    heureDebut: string;
    heureFin: string;
    idPatient: number;
    idPersonnel: number;
    statut?: string;
  }>;
  optimizedPlan: Array<{
    id: number;
    heureDebut: string;
    heureFin: string;
    old_start?: number;
    new_start?: number;
    new_end?: number;
  }>;
  absenceWindow?: {
    start: string;
    end: string;
    interval: 'morning' | 'afternoon' | 'full-day';
  };
  planningContext?: {
    hasPlanning: boolean;
    planningSource: 'planning' | 'default';
    planningWindows: number;
  };
  updatedSchedule: MedicalPlanningAppointment[];
}

@Injectable({
  providedIn: 'root'
})
export class RdvService {

  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getRdvs(): Observable<Rdv[]> {
    return this.http.get<Rdv[]>(`${this.apiUrl}/rdvs`).pipe(
      map((rdvs) =>
        rdvs.map((rdv) => ({
          ...rdv,
          id: Number(
            (rdv as unknown as Record<string, unknown>)['id']
            ?? (rdv as unknown as Record<string, unknown>)['idRdv']
            ?? (rdv as unknown as Record<string, unknown>)['idRDV']
          )
        }))
      )
    );
  }

  getPatientRdvs(): Observable<Rdv[]> {
    return this.http.get<Rdv[]>(`${this.apiUrl}/patient/rdvs`).pipe(
      map((rdvs) =>
        rdvs.map((rdv) => ({
          ...rdv,
          id: Number(
            (rdv as unknown as Record<string, unknown>)['id']
            ?? (rdv as unknown as Record<string, unknown>)['idRdv']
            ?? (rdv as unknown as Record<string, unknown>)['idRDV']
          )
        }))
      )
    );
  }

  deleteRdv(id: number): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/delete_rdv/${id}`);
  }

  updateRdv(rdv: Rdv): Observable<unknown> {
    return this.http.put(`${this.apiUrl}/update_rdv/${rdv.id}`, rdv);
  }

  addRdv(payload: NewRdv): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/add_rdv`, payload);
  }

  confirmAppointmentByDoctor(rdvId: number, idPersonnel?: number): Observable<{
    success: boolean;
    message: string;
    rdv?: Rdv;
    portalUrl?: string;
    emailSent?: boolean;
    emailMessage?: string;
  }> {
    return this.http.post<{
      success: boolean;
      message: string;
      rdv?: Rdv;
      portalUrl?: string;
      emailSent?: boolean;
      emailMessage?: string;
    }>(`${this.apiUrl}/appointments/confirm`, { rdvId, idPersonnel });
  }

  getMedicalStaff(): Observable<MedicalStaff[]> {
    return this.http.get<MedicalStaff[]>(`${this.apiUrl}/medical-staff`).pipe(
      catchError(() =>
        this.http.get<Array<Record<string, unknown>>>(`${this.apiUrl}/users`).pipe(
          map((users) =>
            users
              .filter((u) => {
                const role = Number(u['statut']);
                const specialite = String(u['specialite'] || '').trim();
                return role === 2 || specialite.length > 0;
              })
              .map((u) => ({
                id: Number(u['id']),
                nom: String(u['nom'] || ''),
                prenom: String(u['prenom'] || ''),
                specialite: String(u['specialite'] || 'Generaliste')
              }))
          )
        )
      )
    );
  }

  suggestAvailableSlots(payload: SlotSuggestionRequest): Observable<SlotSuggestionResponse> {
    return this.http.post<SlotSuggestionResponse>(`${this.apiUrl}/suggest-available-slots`, payload, {
      withCredentials: true,
    });
  }

  optimizeAndPersistDoctorPlanning(idPersonnel: number, dateRDV: string): Observable<OptimizePlanningResponse> {
    return this.http.post<OptimizePlanningResponse>(`${this.apiUrl}/medical-staff/optimize-planning`, {
      idPersonnel,
      dateRDV
    });
  }

  cancelAllMedicalStaffDay(idPersonnel: number, dateRDV: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/medical-staff/cancel-all`, { idPersonnel, date: dateRDV });
  }

  recalculateShortDoctorAbsence(
    idPersonnel: number,
    dateRDV: string,
    interval: 'morning' | 'afternoon' | 'full-day',
    absenceHours: number
  ): Observable<ShortAbsenceRecalculationResponse> {
    return this.http.post<ShortAbsenceRecalculationResponse>(`${this.apiUrl}/medical-staff/recalculate-short-absence`, {
      idPersonnel,
      dateRDV,
      interval,
      absenceHours
    });
  }

  getMedicalStaffPlanning(idPersonnel: number, date?: string, rangeDays?: number): Observable<MedicalStaffPlanningResponse> {
    const dateParam = date ? `&date=${encodeURIComponent(date)}` : '';
    const rangeParam = rangeDays ? `&rangeDays=${rangeDays}` : '';
    return this.http.get<MedicalStaffPlanningResponse>(
      `${this.apiUrl}/medical-staff/planning?idPersonnel=${idPersonnel}${dateParam}${rangeParam}`
    );
  }

  getMedicalStaffPatientRecord(
    idPersonnel: number,
    idPatient: number,
    currentRdvId?: number
  ): Observable<MedicalStaffPatientRecordResponse> {
    const currentRdvParam = typeof currentRdvId === 'number' ? `&currentRdvId=${currentRdvId}` : '';
    return this.http.get<MedicalStaffPatientRecordResponse>(
      `${this.apiUrl}/medical-staff/patient-record?idPersonnel=${idPersonnel}&idPatient=${idPatient}${currentRdvParam}`
    );
  }

  getMedicalStaffPatientFullProfile(
    idPersonnel: number,
    idPatient: number,
    currentRdvId?: number
  ): Observable<MedicalStaffPatientFullProfileResponse> {
    const currentRdvParam = typeof currentRdvId === 'number' ? `&currentRdvId=${currentRdvId}` : '';
    return this.http.get<MedicalStaffPatientFullProfileResponse>(
      `${this.apiUrl}/medical-staff/patient-full-profile?idPersonnel=${idPersonnel}&idPatient=${idPatient}${currentRdvParam}`
    );
  }

  getMedicalStaffPatients(idPersonnel: number): Observable<MedicalStaffPatientListItem[]> {
    return this.http.get<MedicalStaffPatientListItem[]>(
      `${this.apiUrl}/medical-staff/patients?idPersonnel=${idPersonnel}`
    );
  }

  findMedicalStaffPatientByCin(idPersonnel: number, cin: string): Observable<MedicalStaffPatientCinSearchResponse> {
    return this.http.get<MedicalStaffPatientCinSearchResponse>(
      `${this.apiUrl}/medical-staff/patient-by-cin?idPersonnel=${idPersonnel}&cin=${encodeURIComponent(cin)}`
    );
  }

  saveMedicalStaffPatient(payload: MedicalStaffPatientSavePayload): Observable<MedicalStaffPatientSaveResponse> {
    return this.http.post<MedicalStaffPatientSaveResponse>(`${this.apiUrl}/medical-staff/patient-save`, payload);
  }

  updateMedicalStaffPatientFullProfile(payload: MedicalStaffPatientProfileUpdatePayload): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(`${this.apiUrl}/medical-staff/patient-full-profile/update`, payload);
  }

  getPatientDashboard(): Observable<PatientDashboardResponse> {
    return this.http.get<PatientDashboardResponse>(`${this.apiUrl}/patient/dashboard`);
  }

  getPatientTodayAccess(patientId?: number): Observable<PatientTodayAccessResponse> {
    let url = `${this.apiUrl}/patient/today-access`;
    if (typeof patientId === 'number') {
      const sep = url.includes('?') ? '&' : '?';
      url = `${url}${sep}patientId=${encodeURIComponent(String(patientId))}`;
    }
    return this.http.get<PatientTodayAccessResponse>(url);
  }

  optimizeSchedule(payload: OptimizeRequest): Observable<OptimizeResponse> {
    return this.http.post<OptimizeResponse>(`${this.apiUrl}/optimize`, payload);
  }

  triggerEmergency(payload: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/medical-staff/emergencies/trigger`, payload);
  }
}

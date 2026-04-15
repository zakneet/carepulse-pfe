import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

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
  agePatient?: number;
  isUrgent?: boolean;
  nom?: string;
  prenom?: string;
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
}

export interface SlotSuggestionResponse {
  dateRDV: string;
  idPersonnel: number;
  isUrgent: boolean;
  slotDuration: number;
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
}

export interface PatientHistoryAppointment {
  id: number;
  dateRDV: string;
  heureDebut: string;
  heureFin?: string;
  motifConsultation?: string;
  statut?: string;
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
    cin: string;
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

  deleteRdv(id: number): Observable<unknown> {
    return this.http.delete(`${this.apiUrl}/delete_rdv/${id}`);
  }

  updateRdv(rdv: Rdv): Observable<unknown> {
    return this.http.put(`${this.apiUrl}/update_rdv/${rdv.id}`, rdv);
  }

  addRdv(payload: NewRdv): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/add_rdv`, payload);
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
    return this.http.post<SlotSuggestionResponse>(`${this.apiUrl}/suggest-available-slots`, payload);
  }

  getMedicalStaffPlanning(idPersonnel: number, date?: string): Observable<MedicalStaffPlanningResponse> {
    const dateParam = date ? `&date=${encodeURIComponent(date)}` : '';
    return this.http.get<MedicalStaffPlanningResponse>(
      `${this.apiUrl}/medical-staff/planning?idPersonnel=${idPersonnel}${dateParam}`
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
}

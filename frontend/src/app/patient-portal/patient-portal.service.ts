import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface PortalPatient {
  id: number;
  nom: string;
  prenom: string;
  fullName: string;
  telephone: string;
  email: string;
}

export interface PortalDoctor {
  id?: number;
  idPersonnel?: number;
  name: string;
  specialite: string;
  clinicName: string;
  address: string;
  phone: string;
  hours: string;
  available: boolean;
  rating?: number | null;
  reviewsCount?: number | null;
  photo?: string | null;
}

export interface PortalAppointment {
  id: number;
  dateRDV: string;
  heureDebut: string;
  heureFin: string;
  motifConsultation: string;
  statut: string;
  doctorName: string;
  specialite: string;
}

export interface PortalDocument {
  id: number;
  type: string;
  title: string;
  createdAt?: string;
}

export interface PortalNotification {
  type: string;
  title: string;
  body: string;
  read: boolean;
}

export interface PatientPortalData {
  token: string;
  patient: PortalPatient;
  doctor: PortalDoctor | null;
  upcomingAppointments: PortalAppointment[];
  appointmentHistory: PortalAppointment[];
  documents: PortalDocument[];
  prescriptions: PortalDocument[];
  notifications: PortalNotification[];
  clinic: { name: string; address: string; mapQuery: string };
  tracking?: {
    weather: any;
    weatherRecommendation: string;
    trafficRecommendation: string;
    trafficDelay: number | null;
    departureTime: string | null;
  } | null;
}

@Injectable({ providedIn: 'root' })
export class PatientPortalService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPortal(token: string): Observable<PatientPortalData> {
    return this.http.get<PatientPortalData>(`${this.apiUrl}/patient/portal/${encodeURIComponent(token)}`);
  }

  getDocument(token: string, docId: number): Observable<{ id: number; title: string; type: string; content: string }> {
    return this.http.get<{ id: number; title: string; type: string; content: string }>(
      `${this.apiUrl}/patient/portal/${encodeURIComponent(token)}/documents/${docId}`
    );
  }
}

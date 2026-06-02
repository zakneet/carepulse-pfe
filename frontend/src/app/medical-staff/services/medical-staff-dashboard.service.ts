import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface DashboardAppointment {
  id: number;
  time: string;
  patient: string;
  motif: string;
  status: string;
  statusColor: string;
  isEmergency: boolean;
}

export interface DashboardEmergencyAlert {
  severity: 'critical' | 'high' | 'info';
  title: string;
  subtitle: string;
  patientName: string;
  time: string;
}

export interface MedicalStaffDashboardResponse {
  idPersonnel: number;
  date: string;
  appointmentsToday: number;
  appointmentsNextHour: number;
  emergencies: number;
  criticalEmergencies: number;
  highEmergencies: number;
  waitingList: number;
  highPriorityWaiting: number;
  optimizationScore: number;
  schedulingEfficiency: number;
  slotUtilization: number;
  autoReplacements: number;
  availableSlots: number;
  occupiedSlots: number;
  occupancyPercent?: number;
  doctorAvailable?: boolean;
  nextAppointment?: DashboardAppointment | null;
  todayAppointments: DashboardAppointment[];
  emergencyAlerts: DashboardEmergencyAlert[];
}

@Injectable({
  providedIn: 'root'
})
export class MedicalStaffDashboardService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDashboard(idPersonnel: number, date?: string): Observable<MedicalStaffDashboardResponse> {
    const dateParam = date ? `&date=${encodeURIComponent(date)}` : '';
    return this.http.get<MedicalStaffDashboardResponse>(
      `${this.apiUrl}/medical-staff/dashboard?idPersonnel=${idPersonnel}${dateParam}`
    );
  }
}

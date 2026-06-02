import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import {
  DashboardAppointment,
  DashboardEmergencyAlert,
  MedicalStaffDashboardResponse
} from './medical-staff-dashboard.service';

export interface WaitingListMatch {
  id: number;
  name: string;
  consultationType: string;
  waitDuration: string;
  waitingDays: number;
  matchPct: number;
  priority: 'High' | 'Moderate' | 'Low';
  freedSlot: string;
}

export interface OptimizationMetric {
  label: string;
  value: number;
  unit: string;
  color: string;
}

export interface OptimizationRecommendation {
  icon: string;
  title: string;
  desc: string;
  action: string;
  type: string;
}

export interface StaffNotification {
  type: string;
  title: string;
  body: string;
  time: string;
  read: boolean;
}

@Injectable({ providedIn: 'root' })
export class MedicalStaffApiService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDashboard(idPersonnel: number, date?: string): Observable<MedicalStaffDashboardResponse & {
    occupancyPercent?: number;
    doctorAvailable?: boolean;
    nextAppointment?: DashboardAppointment | null;
  }> {
    const dateParam = date ? `&date=${encodeURIComponent(date)}` : '';
    return this.http.get<any>(`${this.apiUrl}/medical-staff/dashboard?idPersonnel=${idPersonnel}${dateParam}`);
  }

  getWaitingList(idPersonnel: number): Observable<{ matches: WaitingListMatch[]; count: number; freeSlotsToday: number }> {
    return this.http.get<any>(`${this.apiUrl}/medical-staff/waiting-list?idPersonnel=${idPersonnel}`);
  }

  getOptimization(idPersonnel: number): Observable<{
    score: number;
    metrics: OptimizationMetric[];
    recommendations: OptimizationRecommendation[];
  }> {
    return this.http.get<any>(`${this.apiUrl}/medical-staff/optimization?idPersonnel=${idPersonnel}`);
  }

  getAnalytics(idPersonnel: number, period: 'week' | 'month' | 'quarter' = 'week'): Observable<{
    kpis: Array<{ label: string; value: string; trend: string; color: string }>;
    trend: Array<{ date: string; count: number }>;
  }> {
    return this.http.get<any>(`${this.apiUrl}/medical-staff/analytics?idPersonnel=${idPersonnel}&period=${period}`);
  }

  getNotifications(idPersonnel: number): Observable<{ notifications: StaffNotification[] }> {
    return this.http.get<any>(`${this.apiUrl}/medical-staff/notifications?idPersonnel=${idPersonnel}`);
  }
}

export { DashboardAppointment, DashboardEmergencyAlert, MedicalStaffDashboardResponse };

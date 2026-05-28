import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { MedicalStaff, PatientDashboardResponse, PatientTodayAccessResponse } from '../../services/rdv.service';
import { TravelNoticesResponse } from '../patient-dashboard.models';

@Injectable({ providedIn: 'root' })
export class PatientService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  getDashboard(): Observable<PatientDashboardResponse> {
    return this.http.get<PatientDashboardResponse>(`${this.apiUrl}/patient/dashboard`);
  }

  getTodayAccess(patientId?: number): Observable<PatientTodayAccessResponse> {
    let url = `${this.apiUrl}/patient/today-access`;
    if (typeof patientId === 'number') {
      const params = new HttpParams().set('patientId', String(patientId));
      url = `${url}?${params.toString()}`;
    }
    return this.http.get<PatientTodayAccessResponse>(url);
  }

  getTravelNotices(): Observable<TravelNoticesResponse> {
    return this.http.get<TravelNoticesResponse>(`${this.apiUrl}/patient/travel-notices`).pipe(
      map((response) => ({
        patientId: response.patientId,
        patientAddress: response.patientAddress || '',
        clinicAddress: response.clinicAddress || '',
        notices: response.notices || [],
      }))
    );
  }

  getWeather(city: string): Observable<any> {
    const params = new HttpParams().set('city', city);
    return this.http.get<any>(`${this.apiUrl}/weather`, { params });
  }

  getDoctors(): Observable<MedicalStaff[]> {
    return this.http.get<MedicalStaff[]>(`${this.apiUrl}/medical-staff`);
  }

  getDoctorById(id: number): Observable<MedicalStaff | null> {
    return this.getDoctors().pipe(
      map((doctors) => doctors.find((doctor) => Number(doctor.id) === Number(id)) || null)
    );
  }
}

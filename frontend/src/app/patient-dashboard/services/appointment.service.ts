import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { NewRdv } from '../../services/rdv.service';

@Injectable({ providedIn: 'root' })
export class AppointmentService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  confirmAppointment(payload: NewRdv): Observable<{ message?: string; rdv?: unknown }> {
    return this.http.post<{ message?: string; rdv?: unknown }>(`${this.apiUrl}/add_rdv`, payload);
  }
}

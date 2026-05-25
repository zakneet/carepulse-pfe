import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export type EmergencyType = 'doctor-left-short' | 'doctor-left-long' | 'patient-on-site';
export type DoctorShortEmergencyInterval = 'morning' | 'afternoon' | 'full-day';
export type DoctorLongAbsenceUnit = 'day' | 'week';

export interface EmergencyEventPayload {
  type: EmergencyType;
  interval?: DoctorShortEmergencyInterval;
  absenceHours?: number;
  longAbsenceValue?: number;
  longAbsenceUnit?: DoctorLongAbsenceUnit;
}

@Injectable({
  providedIn: 'root'
})
export class EmergencyEventsService {
  private readonly emergencySubject = new Subject<EmergencyEventPayload>();

  readonly emergency$ = this.emergencySubject.asObservable();

  trigger(event: EmergencyEventPayload): void {
    this.emergencySubject.next(event);
  }
}

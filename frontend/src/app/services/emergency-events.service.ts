import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export type EmergencyType = 'doctor-left-short' | 'doctor-left-long' | 'patient-on-site';

@Injectable({
  providedIn: 'root'
})
export class EmergencyEventsService {
  private readonly emergencySubject = new Subject<EmergencyType>();

  readonly emergency$ = this.emergencySubject.asObservable();

  trigger(type: EmergencyType): void {
    this.emergencySubject.next(type);
  }
}

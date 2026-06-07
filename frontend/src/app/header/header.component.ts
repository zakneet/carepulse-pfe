import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { UserRole } from 'src/app/models/auth.model';
import { AuthService } from 'src/app/services/auth.service';
import { DoctorLongAbsenceUnit, DoctorShortEmergencyInterval, EmergencyEventsService, EmergencyType } from 'src/app/services/emergency-events.service';
import { NotificationService } from 'src/app/services/notification.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit, OnDestroy {
  @Input() emergenciesOnly = false;
  selectedEmergencyType: 'doctor-left-short' | 'doctor-left-long' | 'patient-on-site' | null = null;
  showDoctorShortPopup = false;
  showDoctorLongPopup = false;
  selectedShortInterval: DoctorShortEmergencyInterval = 'morning';
  absenceHours = 1;
  longAbsenceValue = 1;
  longAbsenceUnit: DoctorLongAbsenceUnit = 'day';
  shortEmergencyLoading = false;
  logoPath = 'assets/logo_opticlinic.svg.jpeg';
  isPatientView = false;
  private routerSubscription?: Subscription;
  private shortEmergencyResetTimer?: number;

  constructor(
    private emergencyEvents: EmergencyEventsService,
    private authService: AuthService,
    private router: Router,
    private notifications: NotificationService
  ) { }

  ngOnInit(): void {
    // determine initial view and subscribe to route changes
    this.updateViewFromUrl(this.router.url);
    this.routerSubscription = this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        const nav = event as NavigationEnd;
        this.updateViewFromUrl(nav.urlAfterRedirects || nav.url);
      }
    });
  }

  ngOnDestroy(): void {
    this.routerSubscription?.unsubscribe();
    if (this.shortEmergencyResetTimer) {
      clearTimeout(this.shortEmergencyResetTimer);
    }
  }

  private updateViewFromUrl(url: string): void {
    const clean = (url || '').toLowerCase();
    this.isPatientView = clean.startsWith('/home') || clean.startsWith('/patient');
  }

  onDoctorShortEmergencyClick(): void {
    if (this.shortEmergencyLoading) {
      return;
    }
    console.log('Urgence déclenchée');
    this.notifications.info('Urgence medecin courte: parametrez puis confirmez.');
    this.activateEmergency('doctor-left-short');
  }

  activateEmergency(type: EmergencyType): void {
    console.log('Urgence déclenchée', type);
    if (type === 'doctor-left-short') {
      this.selectedEmergencyType = type;
      this.showDoctorShortPopup = true;
      return;
    }

    if (type === 'doctor-left-long') {
      this.selectedEmergencyType = type;
      this.showDoctorLongPopup = true;
      return;
    }

    this.selectedEmergencyType = type;
    console.log('[Header] activateEmergency', type);

    if (type === 'patient-on-site') {
      if (!this.router.url.includes('/planning')) {
        const baseRoute = this.router.url.includes('/nurse') ? '/medical-staff/nurse' : '/medical-staff/doctor';
        this.router.navigate([baseRoute, 'planning'], { queryParams: { emergency: 'patient-on-site' } });
      }
      
      let idPersonnel = 1;
      const userStr = localStorage.getItem('currentUser');
      if (userStr) {
        try {
          const u = JSON.parse(userStr);
          if (u && u.id) idPersonnel = u.id;
        } catch (e) {}
      }
      
      const now = new Date();
      fetch('http://127.0.0.1:5000/medical-staff/emergencies/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idPersonnel: idPersonnel,
          emergencyType: 'patient-on-site',
          startDateTime: now.toISOString(),
          durationMinutes: 60
        })
      }).then(res => res.json()).then(res => {
         if (res.impactedAppointments && res.impactedAppointments.length > 0) {
            this.notifications.info(`Urgence cabinet activée. ${res.impactedAppointments.length} RDV(s) marqués à reprogrammer.`);
         } else {
            this.notifications.success('Urgence cabinet activée. Aucun RDV n\'a été impacté.');
         }
      });
      return;
    }

    this.emergencyEvents.trigger({ type });
  }

  closeDoctorShortPopup(): void {
    if (this.shortEmergencyLoading) {
      return;
    }
    this.showDoctorShortPopup = false;
  }

  closeDoctorLongPopup(): void {
    if (this.shortEmergencyLoading) {
      return;
    }
    this.showDoctorLongPopup = false;
  }

  confirmDoctorShortEmergency(): void {
    if (this.shortEmergencyLoading) {
      return;
    }
    const safeHours = Number.isFinite(this.absenceHours) ? Math.max(1, Math.min(12, Math.round(this.absenceHours))) : 1;
    this.shortEmergencyLoading = true;
    
    // Attempt to get idPersonnel from auth or path (simplification for this component which lacks direct input)
    let idPersonnel = 1; // Fallback
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        if (u && u.id) idPersonnel = u.id;
      } catch (e) {}
    }

    const durationMinutes = safeHours * 60;
    const now = new Date();
    now.setMinutes(0, 0, 0);

    // Dynamic import to avoid circular dep if any, or just use fetch
    fetch('http://127.0.0.1:5000/medical-staff/emergencies/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        idPersonnel: idPersonnel,
        emergencyType: 'doctor-left-short',
        startDateTime: now.toISOString(),
        durationMinutes: durationMinutes
      })
    }).then(res => res.json()).then(res => {
      this.shortEmergencyLoading = false;
      this.showDoctorShortPopup = false;
      if (res.impactedAppointments && res.impactedAppointments.length > 0) {
        this.notifications.info(`Urgence courte envoyée. ${res.impactedAppointments.length} RDV(s) marqués à reprogrammer.`);
      } else {
        this.notifications.success('Urgence courte envoyée. Aucun RDV n\'a été impacté.');
      }
      this.emergencyEvents.trigger({
        type: 'doctor-left-short',
        interval: this.selectedShortInterval,
        absenceHours: safeHours
      });
    }).catch(err => {
      this.shortEmergencyLoading = false;
      this.notifications.error('Erreur lors du déclenchement de l\'urgence');
      this.showDoctorShortPopup = false;
    });
  }

  setDoctorShortInterval(interval: DoctorShortEmergencyInterval): void {
    this.selectedShortInterval = interval;
  }

  setDoctorLongAbsenceUnit(unit: DoctorLongAbsenceUnit): void {
    this.longAbsenceUnit = unit;
  }

  onLongAbsenceValueChange(rawValue: string): void {
    const parsed = Number(rawValue);
    this.longAbsenceValue = Number.isFinite(parsed) ? parsed : 1;
  }

  confirmDoctorLongEmergency(): void {
    if (this.shortEmergencyLoading) {
      return;
    }

    const maxValue = this.longAbsenceUnit === 'week' ? 12 : 60;
    const safeValue = Number.isFinite(this.longAbsenceValue)
      ? Math.max(1, Math.min(maxValue, Math.round(this.longAbsenceValue)))
      : 1;

    this.shortEmergencyLoading = true;
    
    let idPersonnel = 1;
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        if (u && u.id) idPersonnel = u.id;
      } catch (e) {}
    }

    let durationMinutes = safeValue * 24 * 60;
    if (this.longAbsenceUnit === 'week') {
      durationMinutes *= 7;
    }
    const now = new Date();
    now.setMinutes(0, 0, 0);

    fetch('http://127.0.0.1:5000/medical-staff/emergencies/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        idPersonnel: idPersonnel,
        emergencyType: 'doctor-left-long',
        startDateTime: now.toISOString(),
        durationMinutes: durationMinutes
      })
    }).then(res => res.json()).then(res => {
      this.shortEmergencyLoading = false;
      this.showDoctorLongPopup = false;
      if (res.impactedAppointments && res.impactedAppointments.length > 0) {
        this.notifications.info(`Absence prolongée enregistrée. ${res.impactedAppointments.length} RDV(s) marqués à reprogrammer.`);
      } else {
        this.notifications.success('Absence prolongée enregistrée. Aucun RDV n\'a été impacté aujourd\'hui.');
      }
      this.emergencyEvents.trigger({
        type: 'doctor-left-long',
        longAbsenceValue: safeValue,
        longAbsenceUnit: this.longAbsenceUnit
      });
    }).catch(err => {
      this.shortEmergencyLoading = false;
      this.notifications.error('Erreur lors de la déclaration d\'absence');
      this.showDoctorLongPopup = false;
    });
  }

  onAbsenceHoursChange(rawValue: string): void {
    const parsed = Number(rawValue);
    this.absenceHours = Number.isFinite(parsed) ? parsed : 1;
  }

}

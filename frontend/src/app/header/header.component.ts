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
    console.log('Urgence déclenchée', {
      type: 'doctor-left-short',
      interval: this.selectedShortInterval,
      absenceHours: safeHours
    });
    this.showDoctorShortPopup = false;
    this.emergencyEvents.trigger({
      type: 'doctor-left-short',
      interval: this.selectedShortInterval,
      absenceHours: safeHours
    });
    this.notifications.success('Urgence medecin courte envoyee.');

    if (this.shortEmergencyResetTimer) {
      clearTimeout(this.shortEmergencyResetTimer);
    }

    // Keep a short guard window to avoid duplicate dispatch on repeated clicks.
    this.shortEmergencyResetTimer = window.setTimeout(() => {
      this.shortEmergencyLoading = false;
    }, 1200);
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
    this.showDoctorLongPopup = false;
    console.log('Urgence déclenchée', {
      type: 'doctor-left-long',
      longAbsenceValue: safeValue,
      longAbsenceUnit: this.longAbsenceUnit
    });

    this.emergencyEvents.trigger({
      type: 'doctor-left-long',
      longAbsenceValue: safeValue,
      longAbsenceUnit: this.longAbsenceUnit
    });
    this.notifications.success('Urgence medecin longue envoyee.');

    if (this.shortEmergencyResetTimer) {
      clearTimeout(this.shortEmergencyResetTimer);
    }

    this.shortEmergencyResetTimer = window.setTimeout(() => {
      this.shortEmergencyLoading = false;
    }, 1200);
  }

  onAbsenceHoursChange(rawValue: string): void {
    const parsed = Number(rawValue);
    this.absenceHours = Number.isFinite(parsed) ? parsed : 1;
  }

}

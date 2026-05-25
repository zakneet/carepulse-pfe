import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {
  PatientDashboardAppointment,
  PatientDashboardMedicalRecord,
  PatientDashboardResponse,
  RdvService,
} from '../services/rdv.service';

type AppointmentView = {
  id: number;
  dateLabel: string;
  timeLabel: string;
  doctorLabel: string;
  specialite: string;
  motif: string;
  statut: string;
  statusClass: string;
};

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  loading = true;
  errorMessage = '';
  displayName = 'Patient';
  displayEmail = '';
  initials = 'P';
  statusLabel = 'Patient';
  historyCount = 0;
  appointments: AppointmentView[] = [];
  lastAppointment: AppointmentView | null = null;
  dossierMedical: PatientDashboardMedicalRecord | null = null;

  constructor(
    private readonly authService: AuthService,
    private readonly rdvService: RdvService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.seedProfileFromSession();
    this.loadDashboard();
  }

  goToBooking(): void {
    this.router.navigateByUrl('/patient/booking');
  }

  goToMedicalFile(): void {
    this.router.navigateByUrl('/patient/profile');
  }

  goHome(): void {
    this.router.navigateByUrl('/home');
  }

  goToAppointments(): void {
    this.router.navigateByUrl('/patient/consultations');
  }

  private seedProfileFromSession(): void {
    const currentUser = this.authService.getCurrentUser();
    const prenom = (currentUser?.prenom || '').trim();
    const nom = (currentUser?.nom || '').trim();

    this.displayName = `${prenom} ${nom}`.trim() || 'Patient';
    this.displayEmail = (currentUser?.email || '').trim();
    this.initials = ((prenom[0] || '') + (nom[0] || '')).toUpperCase() || 'P';
  }

  private loadDashboard(): void {
    this.loading = true;
    this.errorMessage = '';

    this.rdvService.getPatientDashboard().subscribe({
      next: (response: PatientDashboardResponse) => {
        this.loading = false;
        this.applyDashboard(response);
      },
      error: (error: unknown) => {
        this.loading = false;
        this.errorMessage = this.getReadableHttpError(error, 'Impossible de charger votre espace patient.');
      }
    });
  }

  private applyDashboard(response: PatientDashboardResponse): void {
    const prenom = (response.patient.prenom || '').trim();
    const nom = (response.patient.nom || '').trim();

    this.displayName = response.patient.nomComplet || `${prenom} ${nom}`.trim() || this.displayName;
    this.displayEmail = (response.patient.email || '').trim() || this.displayEmail;
    this.initials = ((prenom[0] || '') + (nom[0] || '')).toUpperCase() || this.initials;
    this.historyCount = response.historyCount || 0;
    this.dossierMedical = response.dossierMedical;
    this.appointments = (response.appointments || []).map((appointment) => this.mapAppointment(appointment));
    this.lastAppointment = response.lastAppointment ? this.mapAppointment(response.lastAppointment) : this.appointments[0] || null;
  }

  private mapAppointment(appointment: PatientDashboardAppointment): AppointmentView {
    return {
      id: appointment.id,
      dateLabel: this.formatDate(appointment.dateRDV),
      timeLabel: this.formatTimeRange(appointment.heureDebut, appointment.heureFin),
      doctorLabel: this.buildDoctorLabel(appointment),
      specialite: appointment.specialite || 'Generaliste',
      motif: appointment.motifConsultation || '-',
      statut: appointment.statut || 'Programme',
      statusClass: this.getStatusClass(appointment.statut),
    };
  }

  private buildDoctorLabel(appointment: PatientDashboardAppointment): string {
    if (appointment.medecin && appointment.medecin.trim()) {
      return appointment.medecin.trim();
    }

    const prenom = (appointment.medecinPrenom || '').trim();
    const nom = (appointment.medecinNom || '').trim();
    const fullName = `${prenom} ${nom}`.trim();
    return fullName || 'Medecin non renseigne';
  }

  private formatDate(dateValue: string): string {
    const parsed = new Date(`${dateValue.slice(0, 10)}T00:00:00`);
    return Number.isNaN(parsed.getTime()) ? '-' : parsed.toLocaleDateString('fr-FR');
  }

  private formatTimeRange(start?: string, end?: string): string {
    const startLabel = (start || '').slice(0, 5);
    const endLabel = (end || '').slice(0, 5);
    if (startLabel && endLabel) {
      return `${startLabel} - ${endLabel}`;
    }
    return startLabel || endLabel || '-';
  }

  private getStatusClass(status?: string): string {
    const normalized = (status || '').trim().toLowerCase();
    if (normalized.includes('annul')) {
      return 'cancelled';
    }
    if (normalized.includes('report') || normalized.includes('decal')) {
      return 'delayed';
    }
    if (normalized.includes('fait') || normalized.includes('termin') || normalized.includes('effectu')) {
      return 'done';
    }
    return 'scheduled';
  }

  private getReadableHttpError(error: unknown, fallbackMessage: string): string {
    if (error instanceof HttpErrorResponse) {
      const responseError = error.error;
      if (typeof responseError === 'string' && responseError.trim()) {
        return responseError;
      }

      if (responseError && typeof responseError === 'object') {
        const candidate = (responseError as Record<string, unknown>)['message']
          ?? (responseError as Record<string, unknown>)['error'];
        if (typeof candidate === 'string' && candidate.trim()) {
          return candidate;
        }
      }

      if (typeof error.message === 'string' && error.message.trim()) {
        return error.message;
      }
    }

    if (error && typeof error === 'object') {
      const candidate = (error as { error?: unknown; message?: unknown }).error
        ?? (error as { error?: unknown; message?: unknown }).message;
      if (typeof candidate === 'string' && candidate.trim()) {
        return candidate;
      }
    }

    return fallbackMessage;
  }
}

import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {
  MedicalStaff,
  NewRdv,
  PatientDashboardAppointment,
  PatientDashboardMedicalRecord,
  PatientDashboardResponse,
  PatientTodayAccessResponse,
} from '../services/rdv.service';
import { AppointmentService } from '../patient-dashboard/services/appointment.service';
import { PatientService } from '../patient-dashboard/services/patient.service';
import { PlanningService } from '../patient-dashboard/services/planning.service';
import { SingleSlotProposal, TravelNoticeView, WeatherWidgetView } from '../patient-dashboard/patient-dashboard.models';

type AppointmentView = {
  id: number;
  idPersonnel?: number | null;
  dateRDV: string;
  dateLabel: string;
  timeLabel: string;
  doctorLabel: string;
  specialite: string;
  motif: string;
  statut: string;
  statusClass: string;
};

type BookingTarget = {
  doctorId: number;
  specialite: string;
  doctorLabel?: string;
};

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  loading = true;
  errorMessage = '';
  successMessage = '';
  displayName = 'Patient';
  displayEmail = '';
  initials = 'P';
  statusLabel = 'Patient';
  historyCount = 0;
  patientId = 0;
  doctorId: number | null = null;
  doctor: MedicalStaff | null = null;
  hasSecureLink = false;
  selectedDate = '';
  selectedDateLabel = '';
  proposalIndex = 0;
  suggestionLoading = false;
  suggestionError = '';
  suggestion: SingleSlotProposal | null = null;
  travelNotice: TravelNoticeView | null = null;
  weather: WeatherWidgetView | null = null;
  todayAccess: PatientTodayAccessResponse | null = null;
  todayAccessLoading = false;
  bookingLocked = true;
  lockedBookingMessage = 'Le lien sécurisé du médecin est requis pour générer un créneau unique.';
  appointments: AppointmentView[] = [];
  doctorAppointments: AppointmentView[] = [];
  lastAppointment: AppointmentView | null = null;
  nextAppointment: AppointmentView | null = null;
  dossierMedical: PatientDashboardMedicalRecord | null = null;
  dashboardTarget: BookingTarget | null = null;
  doctorPhotoUrl = 'assets/telemedicine_doctor.png';
  doctorAvatar = 'MD';
  doctorSpecialite = 'Cabinet médical';
  doctorFullName = 'Médecin concerné';
  clinicLabel = 'Cabinet médical';
  travelNoticeSummary = 'Aucune notice de trajet pour le moment.';
  weatherLabel = 'Météo indisponible';

  constructor(
    private readonly authService: AuthService,
    private readonly patientService: PatientService,
    private readonly planningService: PlanningService,
    private readonly appointmentService: AppointmentService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.seedProfileFromSession();
    this.doctorId = this.parseDoctorIdFromRoute();
    this.hasSecureLink = this.doctorId !== null;

    if (!this.authService.isAuthenticated() || !this.authService.getToken()) {
      this.loading = false;
      this.errorMessage = '';
      this.suggestionError = '';
      this.bookingLocked = true;
      this.lockedBookingMessage = 'Le dashboard patient nécessite une session connectée pour afficher les données privées.';
      return;
    }

    this.loadDashboard();
  }

  goToBooking(): void {
    const target = this.dashboardTarget || this.buildBookingTargetFromSelection();
    this.router.navigate(['/patient/booking'], {
      queryParams: {
        doctorId: target?.doctorId || null,
        specialite: target?.specialite || null,
      }
    });
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

  confirmSuggestedSlot(): void {
    if (!this.patientId || !this.doctorId || !this.suggestion?.recommendedSlot) {
      return;
    }

    const payload: NewRdv = {
      idPatient: this.patientId,
      idPersonnel: this.doctorId,
      dateRDV: this.selectedDate,
      heureDebut: this.suggestion.recommendedSlot.heureDebut,
      heureFin: this.suggestion.recommendedSlot.heureFin,
      motifConsultation: this.nextAppointment?.motif || 'Consultation de suivi',
      statut: 'Programme',
    };

    this.appointmentService.confirmAppointment(payload).subscribe({
      next: () => {
        this.successMessage = 'Le rendez-vous a été confirmé avec succès.';
        this.proposalIndex = 0;
        this.loadDashboard();
      },
      error: (error: unknown) => {
        this.errorMessage = this.getReadableHttpError(error, 'Impossible de confirmer ce rendez-vous.');
      }
    });
  }

  requestAnotherSuggestion(): void {
    if (!this.doctorId) {
      return;
    }

    this.proposalIndex += 1;
    this.loadSingleSuggestion();
  }

  get liveTrackingLocked(): boolean {
    if (!this.nextAppointment) {
      return true;
    }

    const appointmentDate = this.parseAppointmentDateTime(this.nextAppointment);
    if (!appointmentDate) {
      return true;
    }

    return appointmentDate.getTime() - Date.now() > 2 * 60 * 60 * 1000;
  }

  get liveTrackingMessage(): string {
    if (!this.hasSecureLink) {
      return this.lockedBookingMessage;
    }

    if (!this.nextAppointment) {
      return 'Aucun rendez-vous à suivre pour le moment.';
    }

    if (this.liveTrackingLocked) {
      return 'Le suivi en direct s’active 2h avant votre rendez-vous.';
    }

    return '';
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

    this.patientService.getDashboard().subscribe({
      next: (response: PatientDashboardResponse) => {
        this.loading = false;
        this.applyDashboard(response);
        this.loadSupplementaryData();
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
    this.patientId = response.patient.id;
    this.historyCount = response.historyCount || 0;
    this.dossierMedical = response.dossierMedical;
    this.appointments = (response.appointments || []).map((appointment) => this.mapAppointment(appointment));
    this.applyDoctorContext(response);
    this.doctorAppointments = this.filterAppointmentsForDoctor();
    this.historyCount = this.doctorAppointments.length;
    this.nextAppointment = this.findNextAppointment(this.doctorAppointments);
    this.lastAppointment = this.doctorAppointments[0] || null;
    this.selectedDate = this.buildSelectedDate();
    this.selectedDateLabel = this.formatDate(this.selectedDate);
  }

  private loadSupplementaryData(): void {
    this.bookingLocked = !this.doctorId;

    if (this.doctorId) {
      this.patientService.getDoctorById(this.doctorId).subscribe({
        next: (doctor) => {
          this.doctor = doctor;
          this.loadSingleSuggestion();
        },
        error: () => {
          this.doctor = null;
          this.loadSingleSuggestion();
        }
      });
    } else {
      this.doctor = null;
      this.loadSingleSuggestion();
    }

    this.loadTodayAccess();
    this.loadTravelNotices();
  }

  private loadTodayAccess(): void {
    this.todayAccessLoading = true;
    this.patientService.getTodayAccess(this.patientId || undefined).subscribe({
      next: (response) => {
        this.todayAccess = response;
        this.todayAccessLoading = false;
      },
      error: () => {
        this.todayAccess = null;
        this.todayAccessLoading = false;
      }
    });
  }

  private loadTravelNotices(): void {
    this.patientService.getTravelNotices().subscribe({
      next: (response) => {
        this.travelNotice = this.selectTravelNotice(response.notices);
        this.travelNoticeSummary = this.buildTravelNoticeSummary(this.travelNotice);
        this.loadWeather(response.clinicAddress);
        this.clinicLabel = response.clinicAddress || this.clinicLabel;
      },
      error: () => {
        this.travelNotice = null;
        this.travelNoticeSummary = 'Aucune notice de trajet pour le moment.';
        this.loadWeather();
      }
    });
  }

  private loadWeather(city?: string): void {
    const weatherCity = (city || 'Tunis').trim();
    if (!weatherCity) {
      this.weather = { loading: false, recommendation: 'Météo indisponible', status: 'indisponible' };
      return;
    }

    this.weather = { loading: true, status: weatherCity };
    this.patientService.getWeather(weatherCity).subscribe({
      next: (response) => {
        this.weather = {
          loading: false,
          temperature: response?.current_weather?.temperature ?? undefined,
          windspeed: response?.current_weather?.windspeed ?? undefined,
          recommendation: response?.weather_recommendation || response?.recommendation || null,
          status: weatherCity,
        };
        this.weatherLabel = this.buildWeatherLabel(this.weather);
      },
      error: () => {
        this.weather = { loading: false, recommendation: 'Météo indisponible', status: weatherCity };
        this.weatherLabel = 'Météo indisponible';
      }
    });
  }

  private loadSingleSuggestion(): void {
    if (!this.doctorId) {
      this.bookingLocked = true;
      this.suggestionLoading = false;
      this.suggestion = null;
      this.suggestionError = '';
      this.lockedBookingMessage = 'Le lien sécurisé du médecin est requis pour générer un créneau unique.';
      return;
    }

    this.bookingLocked = false;
    this.suggestionLoading = true;
    this.suggestionError = '';

    this.planningService.suggestSingleSlot(this.doctorId, this.selectedDate, 30, this.proposalIndex).subscribe({
      next: (response) => {
        this.suggestion = response;
        this.suggestionLoading = false;
      },
      error: (error: unknown) => {
        this.suggestionLoading = false;
        this.suggestion = null;
        this.suggestionError = this.getReadableHttpError(error, 'Impossible de générer un créneau unique.');
      }
    });
  }

  private parseDoctorIdFromRoute(): number | null {
    const rawValue = this.route.snapshot.queryParamMap.get('doctorId') || this.route.snapshot.queryParamMap.get('idPersonnel');
    if (!rawValue) {
      return null;
    }

    const parsed = Number(rawValue);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  }

  private buildSelectedDate(): string {
    if (this.nextAppointment?.dateRDV) {
      return this.nextAppointment.dateRDV.slice(0, 10);
    }

    const today = new Date();
    return new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  }

  private selectTravelNotice(notices: TravelNoticeView[]): TravelNoticeView | null {
    if (!notices || notices.length === 0) {
      return null;
    }

    const nextAppointmentNotice = this.nextAppointment
      ? notices.find((notice) => Number(notice.rdvId) === Number(this.nextAppointment?.id))
      : null;

    return nextAppointmentNotice || notices[0] || null;
  }

  private buildTravelNoticeSummary(notice: TravelNoticeView | null): string {
    if (!notice) {
      return 'Aucune notice de trajet pour le moment.';
    }

    const pieces: string[] = [];
    if (notice.notice?.departure_time) {
      pieces.push(`Départ conseillé ${notice.notice.departure_time}`);
    }
    if (notice.notice?.traffic_level) {
      pieces.push(`trafic ${notice.notice.traffic_level}`);
    }
    if (notice.notice?.weather_recommendation) {
      pieces.push(notice.notice.weather_recommendation);
    }
    return pieces.join(' • ') || notice.notice?.message || 'Notice de trajet disponible.';
  }

  private buildWeatherLabel(weather: WeatherWidgetView | null): string {
    if (!weather || weather.loading) {
      return 'Météo indisponible';
    }

    const temperature = typeof weather.temperature === 'number' ? `${Math.round(weather.temperature)}°C` : '';
    const wind = typeof weather.windspeed === 'number' ? `Vent ${Math.round(weather.windspeed)} km/h` : '';
    return [temperature, wind].filter(Boolean).join(' • ') || weather.recommendation || 'Météo indisponible';
  }

  private applyDoctorContext(response: PatientDashboardResponse): void {
    const selectedDoctor = this.pickDoctorFromAppointments(response.appointments || []);
    if (!selectedDoctor) {
      this.dashboardTarget = null;
      this.doctorFullName = 'Médecin concerné';
      this.doctorAvatar = 'MD';
      this.doctorSpecialite = 'Cabinet médical';
      return;
    }

    this.dashboardTarget = selectedDoctor;
    this.doctorFullName = selectedDoctor.doctorLabel || this.doctorFullName;
    this.doctorAvatar = this.buildDoctorAvatar(this.doctorFullName);
    this.doctorSpecialite = selectedDoctor.specialite || 'Cabinet médical';
  }

  private pickDoctorFromAppointments(appointments: PatientDashboardAppointment[]): BookingTarget | null {
    if (this.doctorId) {
      const match = appointments.find((appointment) => Number(appointment.idPersonnel) === Number(this.doctorId));
      if (match) {
        return {
          doctorId: this.doctorId,
          specialite: match.specialite || this.doctor?.specialite || 'Cabinet médical',
          doctorLabel: this.buildDoctorLabel(match),
        };
      }
    }

    if (this.nextAppointment?.idPersonnel) {
      return {
        doctorId: Number(this.nextAppointment.idPersonnel),
        specialite: this.nextAppointment.specialite || this.doctor?.specialite || 'Cabinet médical',
        doctorLabel: this.nextAppointment.doctorLabel || this.doctorFullName,
      };
    }

    return this.doctorId ? {
      doctorId: this.doctorId,
      specialite: this.doctor?.specialite || 'Cabinet médical',
      doctorLabel: this.doctorFullName,
    } : null;
  }

  private buildBookingTargetFromSelection(): BookingTarget | null {
    if (this.dashboardTarget) {
      return this.dashboardTarget;
    }

    if (this.doctorId) {
      return {
        doctorId: this.doctorId,
        specialite: this.doctor?.specialite || this.doctorSpecialite,
      };
    }

    return null;
  }

  private buildDoctorAvatar(label: string): string {
    const parts = label.split(' ').filter(Boolean);
    const first = parts[0]?.charAt(0) || 'M';
    const last = parts.length > 1 ? parts[parts.length - 1].charAt(0) : '';
    return `${first}${last}`.toUpperCase();
  }

  private filterAppointmentsForDoctor(): AppointmentView[] {
    if (this.doctorId) {
      const filtered = this.appointments.filter((appointment) => Number(appointment.idPersonnel || 0) === Number(this.doctorId));
      if (filtered.length > 0) {
        return filtered;
      }
    }

    const doctorName = (this.doctorFullName || '').trim().toLowerCase();
    if (doctorName) {
      return this.appointments.filter((appointment) => appointment.doctorLabel.trim().toLowerCase() === doctorName);
    }

    return this.appointments;
  }

  private findNextAppointment(appointments: AppointmentView[]): AppointmentView | null {
    if (!appointments || appointments.length === 0) {
      return null;
    }

    const sorted = [...appointments].sort((left, right) => this.sortAppointmentByDate(left, right));
    const upcoming = sorted.find((appointment) => this.isFutureAppointment(appointment));
    return upcoming || sorted[0] || null;
  }

  private sortAppointmentByDate(left: AppointmentView, right: AppointmentView): number {
    const leftDate = this.parseAppointmentDateTime(left);
    const rightDate = this.parseAppointmentDateTime(right);
    return (leftDate?.getTime() || 0) - (rightDate?.getTime() || 0);
  }

  private isFutureAppointment(appointment: AppointmentView): boolean {
    const parsed = this.parseAppointmentDateTime(appointment);
    return !!parsed && parsed.getTime() >= Date.now();
  }

  private parseAppointmentDateTime(appointment: AppointmentView): Date | null {
    const datePart = (appointment.dateRDV || '').slice(0, 10);
    const timePart = (appointment.timeLabel || '00:00').split(' - ')[0].slice(0, 5);
    if (!datePart) {
      return null;
    }

    const parsed = new Date(`${datePart}T${timePart}:00`);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  private mapAppointment(appointment: PatientDashboardAppointment): AppointmentView {
    return {
      id: appointment.id,
      idPersonnel: (appointment as PatientDashboardAppointment & { idPersonnel?: number | null }).idPersonnel ?? null,
      dateRDV: appointment.dateRDV,
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

import { Component, ChangeDetectorRef, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, Subscription, forkJoin, of } from 'rxjs';
import { catchError, finalize, switchMap, map } from 'rxjs/operators';
import { AuthService } from 'src/app/services/auth.service';
import { AuthUser } from 'src/app/models/auth.model';
import {
  OptimizePatient,
  OptimizeRequest,
  OptimizedAppointment,
  MedicalStaffPatientRecordResponse,
  MedicalPlanningAppointment,
  MedicalPlanningDay,
  RdvService
} from 'src/app/services/rdv.service';
import { EmergencyEventPayload, EmergencyEventsService } from 'src/app/services/emergency-events.service';
import { NotificationService } from 'src/app/services/notification.service';

interface OptimizedPlanningSlot {
  patientId: number;
  patientDbId: number | null;
  patientName: string;
  motif: string;
  date: string;
  startMinutes: number;
  endMinutes: number;
  startTime: string;
  endTime: string;
  isUrgent: boolean;
}

interface UrgentPatientForm {
  nom: string;
  prenom: string;
  telephone: string;
  cin: string;
  motif: string;
  duration: number;
}

interface UrgentOptimizePatient extends OptimizePatient {
  nom: string;
  prenom: string;
  telephone: string;
  cin: string;
  motif: string;
}

interface UrgentTranslationItem {
  id: number;
  patientName: string;
  previousStart: string;
  previousEnd: string;
  newStart: string;
  newEnd: string;
  deltaMinutes: number;
}

interface UrgentPlanningSummary {
  urgentPatientName: string;
  urgentStart: string;
  urgentEnd: string;
  translatedAppointments: UrgentTranslationItem[];
  recalculatedAt: string;
}

@Component({
  selector: 'app-medical-staff-dashboard',
  templateUrl: './medical-staff-dashboard.component.html',
  styleUrls: ['./medical-staff-dashboard.component.css']
})
export class MedicalStaffDashboardComponent implements OnInit, OnDestroy {

  currentUser: AuthUser | null = null;
  staffView: 'doctor' | 'nurse' = 'doctor';
  baseRoute = '/medical-staff/doctor';
  loading = false;
  errorMessage = '';
  weekStart = '';
  searchQuery = '';
  patientFilter = {
    nom: '',
    prenom: '',
    cin: '',
    email: ''
  };
  selectedDate = this.getTodayLocalISO();
  timeSlots: string[] = this.buildTimeSlots('08:00', '18:00', 30);
  todayPlanning: MedicalPlanningAppointment[] = [];
  weekPlanning: MedicalPlanningDay[] = [];
  optimizerLoading = false;
  optimizerErrorMessage = '';
  optimizedPlanningSlots: OptimizedPlanningSlot[] = [];
  upcomingAppointments: Array<{ id: number; patientName: string; date: string; time: string; status: string }> = [];
  selectedAppointment: MedicalPlanningAppointment | null = null;
  patientRecord: MedicalStaffPatientRecordResponse | null = null;
  patientRecordLoading = false;
  patientRecordError = '';
  patientInConsultation = false;
  showUrgentForm = false;
  urgentFormError = '';
  urgentFormLoading = false;
  urgentPatientForm: UrgentPatientForm = this.createUrgentPatientForm();
  private pendingUrgentPatients: UrgentOptimizePatient[] = [];
  lastUrgentRecalculation: UrgentPlanningSummary | null = null;

  statistics = {
    todayAppointments: 0,
    patientsManaged: 0,
    pendingRequests: 0,
    completedToday: 0
  };

  emergencyNotice = '';
  private activePersonnelId?: number;
  private emergencySub?: Subscription;
  private weekAutoRefreshTimer?: ReturnType<typeof setInterval>;
  private trackedWeekKey = '';
  private refreshSignalHandler = (event: StorageEvent): void => {
    if (event.key === 'planningRefreshSignal') {
      this.loadDashboardData();
    }
  };

  constructor(
    private authService: AuthService,
    private rdvService: RdvService,
    private emergencyEvents: EmergencyEventsService,
    private notifications: NotificationService,
    private changeDetector: ChangeDetectorRef,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.staffView = this.route.snapshot.data['staffView'] === 'nurse' ? 'nurse' : 'doctor';
    this.baseRoute = this.staffView === 'nurse' ? '/medical-staff/nurse' : '/medical-staff/doctor';
    this.trackedWeekKey = this.getWeekKey(this.selectedDate);
    this.loadDashboardData();
    this.startWeekAutoRefresh();
    window.addEventListener('storage', this.refreshSignalHandler);
    this.emergencySub = this.emergencyEvents.emergency$.subscribe((event: EmergencyEventPayload) => {
      if (event.type === 'patient-on-site') {
        this.integrateUrgentPatient();
        return;
      }

      if (event.type === 'doctor-left-short') {
        this.delayCurrentAppointments(Math.max(1, Math.round(event.absenceHours || 1)), event.interval || 'morning');
        return;
      }

      if (event.type === 'doctor-left-long') {
        this.cancelAllAppointments(
          Math.max(1, Math.round(event.longAbsenceValue || 1)),
          event.longAbsenceUnit || 'day'
        );
      }
    });
  }

  ngOnDestroy(): void {
    this.emergencySub?.unsubscribe();
    if (this.weekAutoRefreshTimer) {
      clearInterval(this.weekAutoRefreshTimer);
    }
    window.removeEventListener('storage', this.refreshSignalHandler);
  }

  logout(): void {
    this.authService.logout();
  }

  refreshPlanning(): void {
    this.loadDashboardData();
  }

  private getCurrentPersonnelId(): number | undefined {
    const currentUser = this.currentUser as unknown as {
      id?: number;
      idPersonnel?: number;
      id_personnel?: number;
    } | null;

    return currentUser?.idPersonnel ?? currentUser?.id_personnel ?? this.activePersonnelId ?? currentUser?.id;
  }

  private loadDashboardData(): void {
    this.loading = true;
    this.errorMessage = '';

    const requestedPersonnelId = this.getCurrentPersonnelId();

    this.rdvService.getMedicalStaff().pipe(
      map((staff) => {
        if (requestedPersonnelId && staff.some((member) => member.id === requestedPersonnelId)) {
          return requestedPersonnelId;
        }

        if (staff.length > 0) {
          return staff[0].id;
        }

        return requestedPersonnelId ?? 0;
      }),
      switchMap((idPersonnel) => {
        if (!idPersonnel) {
          throw new Error('Utilisateur medical non identifie.');
        }

        this.activePersonnelId = idPersonnel;

        return this.rdvService.getMedicalStaffPlanning(idPersonnel, this.selectedDate);
      })
    ).subscribe({
      next: (planning) => {
        this.loading = false;
        this.activePersonnelId = Number(planning.idPersonnel || this.activePersonnelId || 0) || this.activePersonnelId;
        this.weekStart = planning.weekStart || '';
        this.trackedWeekKey = this.weekStart || this.getWeekKey(this.selectedDate);
        this.todayPlanning = planning.todayPlanning || [];
        this.weekPlanning = planning.weekPlanning || [];
        this.applyMetrics();
        this.loadOptimizedPlanning();
      },
      error: (error) => {
        this.loading = false;
        const errorMsg = this.getReadableHttpError(error, 'Impossible de charger le planning du personnel de sante.');
        console.error('Erreur chargement planning:', errorMsg);
        this.errorMessage = errorMsg;
        this.notifications.error(errorMsg);
      }
    });
  }

  getOptimizedSlotForCell(dayDate: string, slot: string): OptimizedPlanningSlot | null {
    if (dayDate !== this.selectedDate) {
      return null;
    }

    const slotStart = this.toMinutes(slot);
    const slotEnd = slotStart + 30;

    for (const item of this.optimizedPlanningSlots) {
      if (item.date !== dayDate) {
        continue;
      }

      if (slotStart >= item.startMinutes && slotEnd <= item.endMinutes) {
        return item;
      }
    }

    return null;
  }

  openOptimizedSlotDetails(slot: OptimizedPlanningSlot): void {
    const resolvedPatientId = typeof slot.patientDbId === 'number' ? slot.patientDbId : slot.patientId;
    const idPersonnel = this.getCurrentPersonnelId();
    this.selectedAppointment = {
      id: slot.patientId,
      idPatient: resolvedPatientId,
      idPersonnel,
      dateRDV: slot.date,
      heureDebut: `${slot.startTime}:00`,
      heureFin: `${slot.endTime}:00`,
      motifConsultation: `${slot.motif} (optimise)`,
      statut: 'Planning optimise',
      patientNom: slot.patientName,
      patientPrenom: '',
    };
    this.patientRecord = null;
    this.patientRecordLoading = false;
    if (typeof slot.patientDbId === 'number') {
      this.patientRecordError = '';
      const idPersonnel = this.getCurrentPersonnelId();
      if (!idPersonnel) {
        this.patientRecordError = 'Utilisateur medical non identifie.';
        this.patientInConsultation = true;
        return;
      }

      this.patientRecordLoading = true;
      this.patientInConsultation = true;
      // Do not pass currentRdvId for optimized slots because the slot can move in time.
      this.loadPatientRecord(idPersonnel, slot.patientDbId);
      return;
    }

    this.patientRecordError = 'Profil indisponible pour ce patient de test (non present en base).';
    this.patientInConsultation = true;
  }

  private applyMetrics(): void {
    // Compute simple dashboard metrics
    this.statistics.todayAppointments = (this.todayPlanning || []).length;

    const allWeekAppointments = this.weekPlanning.flatMap((d) => d.appointments || []);
    const uniquePatients = new Set<number>();
    for (const rdv of allWeekAppointments) {
      const pid = Number((rdv as any).idPatient);
      if (!Number.isNaN(pid)) {
        uniquePatients.add(pid);
      }
    }

    this.statistics.patientsManaged = uniquePatients.size;
    this.statistics.pendingRequests = allWeekAppointments.filter((a) => (a.statut || '').toLowerCase().includes('attente') || (a.statut || '').toLowerCase().includes('pending')).length;
    this.statistics.completedToday = allWeekAppointments.filter((a) => (a.statut || '').toLowerCase().includes('termine') || (a.statut || '').toLowerCase().includes('completed')).length;
  }

  appointmentCin(appointment: MedicalPlanningAppointment): string {
    return this.getAppointmentCin(appointment) || '-';
  }

  appointmentEmail(appointment: MedicalPlanningAppointment): string {
    return this.getAppointmentEmail(appointment) || '-';
  }

  openAppointmentDetails(appointment: MedicalPlanningAppointment): void {
    const idPatient = appointment.idPatient;
    const idPersonnel = this.getCurrentPersonnelId();

    if (typeof idPatient !== 'number' || !idPersonnel) {
      this.selectedAppointment = appointment;
      this.patientRecord = null;
      this.patientRecordError = 'Impossible de charger le dossier patient pour ce rendez-vous.';
      this.patientRecordLoading = false;
      this.patientInConsultation = true;
      return;
    }

    this.selectedAppointment = appointment;
    this.patientRecord = null;
    this.patientRecordError = '';
    this.patientRecordLoading = true;
    this.patientInConsultation = true;

    this.loadPatientRecord(idPersonnel, idPatient, appointment.id);
  }

  private loadPatientRecord(idPersonnel: number, idPatient: number, currentRdvId?: number): void {
    this.rdvService
      .getMedicalStaffPatientRecord(idPersonnel, idPatient, currentRdvId)
      .pipe(finalize(() => {
        this.patientRecordLoading = false;
      }))
      .subscribe({
        next: (record) => {
          this.patientRecord = record;
          this.patientRecordError = '';
        },
        error: () => {
          this.patientRecord = null;
          this.patientRecordError = 'Impossible de charger le profil et le dossier medical du patient.';
        }
      });
  }

  closePatientRecord(): void {
    this.selectedAppointment = null;
    this.patientRecord = null;
    this.patientRecordError = '';
    this.patientRecordLoading = false;
    this.patientInConsultation = false;
  }

  toggleConsultationPresence(): void {
    this.patientInConsultation = !this.patientInConsultation;
  }

  openPatientFullProfile(): void {
    const idPatient = this.selectedAppointment?.idPatient;
    if (typeof idPatient !== 'number') {
      this.patientRecordError = 'Impossible de rediriger vers le profil complet du patient.';
      return;
    }

    this.router.navigate([this.baseRoute, 'patient-profile', idPatient], {
      queryParams: {
        rdvId: this.selectedAppointment?.id
      }
    });
  }

  get selectedAppointmentPatientName(): string {
    if (this.patientRecord?.patient) {
      const prenom = (this.patientRecord.patient.prenom || '').trim();
      const nom = (this.patientRecord.patient.nom || '').trim();
      const fullName = `${prenom} ${nom}`.trim();
      if (fullName) {
        return fullName;
      }
    }
    if (this.selectedAppointment) {
      return this.buildPatientName(this.selectedAppointment);
    }

    return 'Patient';
  }

  patientLabel(appointment: MedicalPlanningAppointment | null | undefined): string {
    if (!appointment) {
      return 'Patient';
    }
    const prenom = (appointment.patientPrenom || '').trim();
    const nom = (appointment.patientNom || '').trim();
    const full = `${prenom} ${nom}`.trim();
    return full || 'Patient';
  }

  buildDoctorName(item: { medecinPrenom?: string; medecinNom?: string; medecin?: string } | null | undefined): string {
    if (!item) return 'Medecin non renseigne';
    const prenom = (item.medecinPrenom || '').trim();
    const nom = (item.medecinNom || '').trim();
    const fullName = `${prenom} ${nom}`.trim();
    if (fullName) return fullName;
    if (item.medecin && String(item.medecin).trim()) return String(item.medecin).trim();
    return 'Medecin non renseigne';
  }

  openUrgentForm(): void {
    this.urgentPatientForm = this.createUrgentPatientForm();
    this.urgentFormError = '';
    this.showUrgentForm = true;
  }

  closeUrgentForm(): void {
    if (this.urgentFormLoading) {
      return;
    }

    this.showUrgentForm = false;
    this.urgentFormError = '';
  }

  submitUrgentPatientForm(): void {
    const urgentPatient = this.buildUrgentPatientPayload();
    if (!urgentPatient) {
      return;
    }

    this.pendingUrgentPatients = [urgentPatient];
    this.showUrgentForm = false;
    this.urgentFormError = '';
    this.urgentFormLoading = true;
    this.emergencyNotice = 'Urgence patient saisie: recalcul OR-Tools en cours...';
    this.loadOptimizedPlanning(true);
  }

  formatShortDate(value: string | undefined): string {
    if (!value) {
      return '-';
    }

    const parsed = new Date(`${value}T00:00:00`);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }

    return parsed.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  formatShortTime(value: string | undefined): string {
    if (!value) {
      return '-';
    }

    return value.slice(0, 5);
  }

  clearPatientFilter(): void {
    this.patientFilter = { nom: '', prenom: '', cin: '', email: '' };
  }

  get weekPlanningRows(): Array<{ date: string; label: string }> {
    if (!this.weekStart) {
      const fallback = this.selectedDate || this.getTodayLocalISO();
      return [{ date: fallback, label: this.formatDayLabel(fallback) }];
    }

    const start = new Date(`${this.weekStart}T00:00:00`);
    if (Number.isNaN(start.getTime())) {
      return [{ date: this.selectedDate, label: this.formatDayLabel(this.selectedDate) }];
    }

    const rows: Array<{ date: string; label: string }> = [];
    for (let i = 0; i < 7; i += 1) {
      const current = new Date(start);
      current.setDate(start.getDate() + i);
      const date = this.formatDateLocal(current);
      rows.push({ date, label: this.formatDayLabel(date) });
    }
    return rows;
  }

  getAppointmentForSlot(dayDate: string, slot: string): MedicalPlanningAppointment | null {
    const day = this.weekPlanning.find((d) => (d.date || '').slice(0, 10) === dayDate);
    if (!day || !day.appointments || day.appointments.length === 0) {
      return null;
    }

    const slotStart = this.toMinutes(slot);
    const slotEnd = slotStart + 30;

    for (const appointment of day.appointments) {
      if (!this.matchesPatientFilter(appointment) || !this.matchesSearch(appointment)) {
        continue;
      }

      const start = this.toMinutes((appointment.heureDebut || '').slice(0, 5));
      const endRaw = (appointment.heureFin || '').slice(0, 5);
      const end = endRaw ? this.toMinutes(endRaw) : start + 30;

      if (slotStart >= start && slotEnd <= end) {
        return appointment;
      }
    }

    return null;
  }

  private normalize(value: unknown): string {
    return String(value || '').trim().toLowerCase();
  }

  private matchesSearch(appointment: MedicalPlanningAppointment): boolean {
    const query = this.normalize(this.searchQuery);
    if (!query) {
      return true;
    }

    const patientNom = this.normalize(appointment.patientNom);
    const patientPrenom = this.normalize(appointment.patientPrenom);
    const patientCin = this.normalize(this.getAppointmentCin(appointment));
    const patientEmail = this.normalize(this.getAppointmentEmail(appointment));
    const motif = this.normalize(appointment.motifConsultation);
    const status = this.normalize(appointment.statut);

    return [patientNom, patientPrenom, patientCin, patientEmail, motif, status].some((value) => value.includes(query));
  }

  private matchesPatientFilter(appointment: MedicalPlanningAppointment): boolean {
    const nom = this.normalize(this.patientFilter.nom);
    const prenom = this.normalize(this.patientFilter.prenom);
    const cin = this.normalize(this.patientFilter.cin);
    const email = this.normalize(this.patientFilter.email);

    if (!nom && !prenom && !cin && !email) {
      return true;
    }

    const patientNom = this.normalize(appointment.patientNom);
    const patientPrenom = this.normalize(appointment.patientPrenom);
    const patientCin = this.normalize(this.getAppointmentCin(appointment));
    const patientEmail = this.normalize(this.getAppointmentEmail(appointment));

    const matchNom = !nom || patientNom.includes(nom);
    const matchPrenom = !prenom || patientPrenom.includes(prenom);
    const matchCin = !cin || patientCin.includes(cin);
    const matchEmail = !email || patientEmail.includes(email);
    return matchNom && matchPrenom && matchCin && matchEmail;
  }

  private formatDayLabel(dateValue: string): string {
    const parsed = new Date(`${dateValue}T00:00:00`);
    if (Number.isNaN(parsed.getTime())) {
      return dateValue;
    }

    return parsed.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: '2-digit',
      month: '2-digit'
    });
  }

  private startWeekAutoRefresh(): void {
    this.weekAutoRefreshTimer = setInterval(() => {
      const today = this.getTodayLocalISO();
      const currentWeekKey = this.getWeekKey(today);

      if (currentWeekKey !== this.trackedWeekKey) {
        this.selectedDate = today;
        this.trackedWeekKey = currentWeekKey;
        this.loadDashboardData();
      }
    }, 60 * 1000);
  }

  private getWeekKey(dateValue: string): string {
    const parsed = new Date(`${dateValue}T00:00:00`);
    if (Number.isNaN(parsed.getTime())) {
      return dateValue;
    }

    const mondayOffset = parsed.getDay() === 0 ? -6 : 1 - parsed.getDay();
    parsed.setDate(parsed.getDate() + mondayOffset);
    return this.formatDateLocal(parsed);
  }

  private getTodayLocalISO(): string {
    return this.formatDateLocal(new Date());
  }

  private formatDateLocal(value: Date): string {
    const year = value.getFullYear();
    const month = `${value.getMonth() + 1}`.padStart(2, '0');
    const day = `${value.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private buildTimeSlots(start: string, end: string, stepMinutes: number): string[] {
    const startMinutes = this.toMinutes(start);
    const endMinutes = this.toMinutes(end);

    const slots: string[] = [];
    for (let cursor = startMinutes; cursor < endMinutes; cursor += stepMinutes) {
      const hh = Math.floor(cursor / 60)
        .toString()
        .padStart(2, '0');
      const mm = (cursor % 60).toString().padStart(2, '0');
      slots.push(`${hh}:${mm}`);
    }

    return slots;
  }

  private toMinutes(value: string): number {
    const [hh, mm] = value.split(':');
    const hour = Number(hh || 0);
    const minute = Number(mm || 0);
    return hour * 60 + minute;
  }

  private getAppointmentCin(appointment: MedicalPlanningAppointment): string {
    const cin = (appointment as unknown as Record<string, unknown>)['patientCin'];
    return String(cin || '').trim();
  }

  private getAppointmentEmail(appointment: MedicalPlanningAppointment): string {
    const email = (appointment as unknown as Record<string, unknown>)['patientEmail'];
    return String(email || '').trim();
  }

  private buildPatientName(appointment: MedicalPlanningAppointment): string {
    const prenom = (appointment.patientPrenom || '').trim();
    const nom = (appointment.patientNom || '').trim();
    const fullName = `${prenom} ${nom}`.trim();

    if (fullName) {
      return fullName;
    }

    return `Patient #${appointment.idPatient ?? 'N/A'}`;
  }

  private loadOptimizedPlanning(integrateIntoPlanning = false): void {
    const sourceAppointments = [...this.todayPlanning];
    const payload = this.buildOptimizePayload(this.pendingUrgentPatients, sourceAppointments);
    if (!payload || payload.patients.length === 0) {
      this.optimizedPlanningSlots = [];
      this.optimizerErrorMessage = '';
      return;
    }

    this.optimizerLoading = true;
    this.optimizerErrorMessage = '';

    const patientsById = new Map<number, OptimizePatient>();
    payload.patients.forEach((patient) => {
      patientsById.set(patient.id, patient);
    });

    this.rdvService.optimizeSchedule(payload).pipe(
      finalize(() => {
        this.optimizerLoading = false;
        this.urgentFormLoading = false;
      })
    ).subscribe({
      next: (response) => {
        if (response.status !== 'success') {
          this.optimizedPlanningSlots = [];
          this.optimizerErrorMessage = response.message || 'Aucune optimisation disponible.';
          this.urgentFormLoading = false;
          return;
        }

        const optimizedData = Array.isArray(response.data) ? response.data : [];
        this.optimizedPlanningSlots = (optimizedData).map((item: OptimizedAppointment) => {
          const patient = patientsById.get(item.patient_id);
          const patientName = `${patient?.prenom || ''} ${patient?.nom || ''}`.trim() || `Patient #${item.patient_id}`;
          return {
            patientId: item.patient_id,
            patientDbId: typeof patient?.patientDbId === 'number' ? patient.patientDbId : null,
            patientName,
            motif: patient?.motif || 'Consultation',
            date: this.selectedDate,
            startMinutes: item.start,
            endMinutes: item.end,
            startTime: this.minutesToHour(item.start),
            endTime: this.minutesToHour(item.end),
            isUrgent: Boolean(patient?.isUrgent),
          };
        });

        if (integrateIntoPlanning && this.pendingUrgentPatients.length > 0) {
          this.persistOptimizedUrgentPlanning(optimizedData, patientsById, sourceAppointments);
        } else {
          this.urgentFormLoading = false;
        }
      },
      error: (error) => {
        this.optimizedPlanningSlots = [];
        this.optimizerErrorMessage = this.getReadableHttpError(error, 'Impossible de charger le planning optimise.');
        this.urgentFormLoading = false;
      }
    });
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

  private buildOptimizePayload(extraPatients: OptimizePatient[] = [], sourceAppointments: MedicalPlanningAppointment[] = this.todayPlanning): OptimizeRequest | null {
    const doctorStart = 8 * 60;
    const doctorEnd = 18 * 60;

    const urgentPatients = extraPatients.filter((patient) => typeof patient.id === 'number');

    if (sourceAppointments.length === 0 && urgentPatients.length === 0) {
      const fallbackPatients: OptimizePatient[] = [
        { id: 9001, nom: 'Test', prenom: 'Patient 1', motif: 'Consultation', start: 540, end: 720, duration: 30 },
        { id: 9002, nom: 'Test', prenom: 'Patient 2', motif: 'Controle', start: 570, end: 780, duration: 30 },
        { id: 9003, nom: 'Test', prenom: 'Patient 3', motif: 'Suivi', start: 600, end: 840, duration: 30 },
      ];
      return {
        patients: fallbackPatients,
        doctor_schedule: { start: doctorStart, end: doctorEnd }
      };
    }

    const patients: OptimizePatient[] = [...urgentPatients];
    for (const appointment of sourceAppointments) {
      const startRaw = (appointment.heureDebut || '').slice(0, 5);
      if (!startRaw) {
        continue;
      }

      const startMinute = this.toMinutes(startRaw);
      const endRaw = (appointment.heureFin || '').slice(0, 5);
      const endMinute = endRaw ? this.toMinutes(endRaw) : startMinute + 30;
      const duration = Math.max(15, endMinute - startMinute);

      const windowStart = Math.max(doctorStart, startMinute - 60);
      const windowEnd = Math.min(doctorEnd, startMinute + 180);
      if (windowEnd - windowStart < duration) {
        continue;
      }

      patients.push({
        id: Number(appointment.id),
        patientDbId: typeof appointment.idPatient === 'number' ? appointment.idPatient : undefined,
        nom: (appointment.patientNom || '').trim(),
        prenom: (appointment.patientPrenom || '').trim(),
        motif: appointment.motifConsultation || 'Consultation',
        start: windowStart,
        end: windowEnd,
        duration,
      });
    }

    if (patients.length === 0) {
      return null;
    }

    return {
      patients,
      doctor_schedule: { start: doctorStart, end: doctorEnd }
    };
  }

  private persistOptimizedUrgentPlanning(
    optimizedData: OptimizedAppointment[],
    patientsById: Map<number, OptimizePatient>,
    sourceAppointments: MedicalPlanningAppointment[]
  ): void {
    const idPersonnel = this.getCurrentPersonnelId();
    const urgentPatient = this.pendingUrgentPatients.find((patient) => Boolean(patient.isUrgent)) || null;
    const responseById = new Map<number, OptimizedAppointment>();
    optimizedData.forEach((item) => {
      responseById.set(Number(item.patient_id), item);
    });

    const updatedAppointments = sourceAppointments
      .map((appointment) => {
        const optimized = responseById.get(Number(appointment.id));
        if (!optimized) {
          return appointment;
        }

        return {
          ...appointment,
          heureDebut: this.minutesToHour(optimized.start),
          heureFin: this.minutesToHour(optimized.end)
        };
      })
      .sort((a, b) => this.toMinutes((a.heureDebut || '').slice(0, 5)) - this.toMinutes((b.heureDebut || '').slice(0, 5)));

    const urgentOptimized = urgentPatient ? responseById.get(urgentPatient.id) || null : null;
    const urgentAppointment = urgentPatient && urgentOptimized ? {
      id: urgentPatient.id,
      idPatient: undefined,
      idPersonnel,
      dateRDV: this.selectedDate,
      heureDebut: this.minutesToHour(urgentOptimized.start),
      heureFin: this.minutesToHour(urgentOptimized.end),
      motifConsultation: urgentPatient.motif || 'Urgence patient',
      statut: 'urgence',
      patientNom: urgentPatient.nom,
      patientPrenom: urgentPatient.prenom,
    } as MedicalPlanningAppointment : null;

    const combinedAppointments = urgentAppointment
      ? [...updatedAppointments, urgentAppointment].sort((a, b) => this.toMinutes((a.heureDebut || '').slice(0, 5)) - this.toMinutes((b.heureDebut || '').slice(0, 5)))
      : updatedAppointments;

    this.lastUrgentRecalculation = this.buildUrgentPlanningSummary(
      urgentPatient,
      urgentAppointment,
      sourceAppointments,
      optimizedData,
      responseById
    );

    this.todayPlanning = [...combinedAppointments];
    this.weekPlanning = this.weekPlanning.map((day) => {
      if ((day.date || '').slice(0, 10) !== this.selectedDate) {
        return day;
      }

      return {
        ...day,
        appointments: [...combinedAppointments],
        count: combinedAppointments.length
      };
    });

    this.selectedAppointment = urgentAppointment;
    this.applyMetrics();
    this.changeDetector.markForCheck();

    const updateRequests = sourceAppointments.map((appointment) => {
      const optimized = responseById.get(Number(appointment.id));
      if (!optimized) {
        return of(null);
      }

      return this.rdvService.updateRdv({
        id: appointment.id,
        idPatient: appointment.idPatient,
        idPersonnel: appointment.idPersonnel,
        dateRDV: appointment.dateRDV,
        heureDebut: this.minutesToHour(optimized.start),
        heureFin: this.minutesToHour(optimized.end),
        motifConsultation: appointment.motifConsultation || 'consultation'
      }).pipe(catchError(() => of(null)));
    });

    let urgentRequest: Observable<unknown> = of(null);
    if (urgentPatient && urgentAppointment && idPersonnel) {
      urgentRequest = this.rdvService.saveMedicalStaffPatient({
        idPersonnel,
        patient: {
          nom: urgentPatient.nom,
          prenom: urgentPatient.prenom,
          cin: urgentPatient.cin,
          telephone: urgentPatient.telephone,
          email: null,
        }
      }).pipe(
        switchMap((saveResponse) => {
          const savedPatientId = Number(saveResponse?.patient?.id || 0);
          return this.rdvService.addRdv({
            idPatient: savedPatientId,
            idPersonnel,
            dateRDV: urgentAppointment.dateRDV,
            heureDebut: urgentAppointment.heureDebut,
            heureFin: urgentAppointment.heureFin,
            motifConsultation: urgentAppointment.motifConsultation || urgentPatient.motif || 'Urgence patient',
            statut: 'consultation',
            nom: urgentPatient.nom,
            prenom: urgentPatient.prenom,
            telephone: urgentPatient.telephone,
            isUrgent: true,
          }).pipe(
            switchMap((creationResponse) => {
              const createdId = this.extractCreatedRdvId(creationResponse);
              if (!createdId) {
                return of(null);
              }

              return this.rdvService.updateRdv({
                id: createdId,
                idPatient: savedPatientId,
                idPersonnel,
                dateRDV: urgentAppointment.dateRDV,
                heureDebut: urgentAppointment.heureDebut,
                heureFin: urgentAppointment.heureFin,
                motifConsultation: urgentAppointment.motifConsultation || urgentPatient.motif || 'Urgence patient',
                statut: 'urgence'
              }).pipe(catchError(() => of(null)));
            }),
            catchError(() => of(null))
          );
        }),
        catchError(() => of(null))
      );
    }

    forkJoin([...updateRequests, urgentRequest]).subscribe({
      next: (results) => {
        const failed = results.filter((result) => result === null).length;
        if (failed > 0) {
          this.emergencyNotice = 'Urgence patient integree localement, mais une partie de la sauvegarde a echoue.';
        } else {
          this.emergencyNotice = 'Urgence patient integree au planning et recalcul OR-Tools enregistre.';
        }

        this.pendingUrgentPatients = [];
        this.urgentFormLoading = false;
        this.loadDashboardData();
      },
      error: () => {
        this.emergencyNotice = 'Urgence patient integree localement, mais la sauvegarde a echoue.';
        this.urgentFormLoading = false;
      }
    });
  }

  private extractCreatedRdvId(response: unknown): number | null {
    if (!response || typeof response !== 'object') {
      return null;
    }

    const rdv = (response as { rdv?: Record<string, unknown> }).rdv;
    if (!rdv) {
      return null;
    }

    const candidate = rdv['id'] ?? rdv['idRDV'] ?? rdv['idRdv'];
    const id = Number(candidate);
    return Number.isFinite(id) && id > 0 ? id : null;
  }

  private buildUrgentPlanningSummary(
    urgentPatient: UrgentOptimizePatient | null,
    urgentAppointment: MedicalPlanningAppointment | null,
    sourceAppointments: MedicalPlanningAppointment[],
    optimizedData: OptimizedAppointment[],
    responseById: Map<number, OptimizedAppointment>
  ): UrgentPlanningSummary | null {
    if (!urgentPatient || !urgentAppointment) {
      return null;
    }

    const translatedAppointments = sourceAppointments
      .map((appointment) => {
        const optimized = responseById.get(Number(appointment.id));
        if (!optimized) {
          return null;
        }

        const previousStart = (appointment.heureDebut || '').slice(0, 5);
        const previousEnd = (appointment.heureFin || '').slice(0, 5);
        const newStart = this.minutesToHour(optimized.start);
        const newEnd = this.minutesToHour(optimized.end);
        const deltaMinutes = this.toMinutes(newStart) - this.toMinutes(previousStart);

        if (previousStart === newStart && previousEnd === newEnd) {
          return null;
        }

        return {
          id: Number(appointment.id),
          patientName: this.buildPatientName(appointment),
          previousStart,
          previousEnd,
          newStart,
          newEnd,
          deltaMinutes,
        };
      })
      .filter((item): item is UrgentTranslationItem => item !== null)
      .sort((a, b) => a.newStart.localeCompare(b.newStart));

    return {
      urgentPatientName: `${urgentPatient.prenom} ${urgentPatient.nom}`.trim() || 'Patient urgent',
      urgentStart: (urgentAppointment.heureDebut || '').slice(0, 5),
      urgentEnd: (urgentAppointment.heureFin || '').slice(0, 5),
      translatedAppointments,
      recalculatedAt: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    };
  }

  private integrateUrgentPatient(): void {
    this.openUrgentForm();
  }

  private createUrgentPatientForm(): UrgentPatientForm {
    return {
      nom: '',
      prenom: '',
      telephone: '',
      cin: '',
      motif: 'Urgence patient',
      duration: 30,
    };
  }

  private buildUrgentPatientPayload(): UrgentOptimizePatient | null {
    const nom = this.urgentPatientForm.nom.trim();
    const prenom = this.urgentPatientForm.prenom.trim();
    const telephone = this.urgentPatientForm.telephone.trim();
    const cin = this.urgentPatientForm.cin.trim();
    const motif = this.urgentPatientForm.motif.trim() || 'Urgence patient';
    const duration = Math.max(15, Math.floor(Number(this.urgentPatientForm.duration)) || 0);

    if (!nom || !prenom || !telephone || !cin) {
      this.urgentFormError = 'Veuillez remplir le nom, le prénom, le téléphone et le CIN.';
      return null;
    }

    if (duration < 15) {
      this.urgentFormError = 'La durée doit être au moins de 15 minutes.';
      return null;
    }

    const urgentPatientId = Date.now();

    return {
      id: urgentPatientId,
      nom,
      prenom,
      telephone,
      cin,
      motif,
      start: 8 * 60,
      end: 18 * 60,
      duration,
      priority: 1000,
      isUrgent: true,
    };
  }

  private normalizeStatus(value: string | undefined): string {
    return (value || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  isDelayedStatus(value: string | undefined): boolean {
    return this.normalizeStatus(value).includes('decale');
  }

  isCancelledStatus(value: string | undefined): boolean {
    return this.normalizeStatus(value).includes('annule');
  }

  private delayCurrentAppointments(absenceHours: number, interval: 'morning' | 'afternoon' | 'full-day'): void {
    const idPersonnel = this.getCurrentPersonnelId();
    const date = this.selectedDate || this.getTodayLocalISO();

    if (!idPersonnel) {
      this.emergencyNotice = 'Utilisateur medical non identifie.';
      return;
    }

    this.optimizerLoading = true;
    this.rdvService.recalculateShortDoctorAbsence(idPersonnel, date, interval, absenceHours).pipe(
      finalize(() => {
        this.optimizerLoading = false;
      })
    ).subscribe({
      next: (response) => {
        const intervalLabel = interval === 'morning' ? 'matin' : interval === 'afternoon' ? 'apres-midi' : 'toute la journee';
        this.emergencyNotice = response.message || `Urgence patient: planning recalcule sur ${intervalLabel} pendant ${absenceHours} heure(s).`;
        this.notifications.success(this.emergencyNotice);

        // If backend returned an updated schedule, apply it locally immediately
        if (response && Array.isArray(response.updatedSchedule) && response.updatedSchedule.length > 0) {
          const updated = response.updatedSchedule as MedicalPlanningAppointment[];
          this.todayPlanning = [...updated];
          this.weekPlanning = this.weekPlanning.map((day) => {
            if ((day.date || '').slice(0, 10) !== this.selectedDate) {
              return day;
            }

            return {
              ...day,
              appointments: [...updated],
              count: updated.length,
            };
          });

          this.applyMetrics();
          this.changeDetector.markForCheck();
          // allow visual update, then refresh full data from server
          window.setTimeout(() => this.loadDashboardData(), 200);
          return;
        }

        this.loadDashboardData();
      },
      error: (err) => {
        this.emergencyNotice = this.getReadableHttpError(err, 'Erreur: Impossible de recalculer le planning.');
        this.notifications.error(this.emergencyNotice);
      }
    });
  }

  private getDoctorShortEmergencyWindow(interval: 'morning' | 'afternoon' | 'full-day'): { start: number; end: number } {
    if (interval === 'afternoon') {
      return { start: this.toMinutes('12:00'), end: this.toMinutes('18:00') };
    }

    if (interval === 'full-day') {
      return { start: this.toMinutes('08:00'), end: this.toMinutes('18:00') };
    }

    return { start: this.toMinutes('08:00'), end: this.toMinutes('12:00') };
  }

  private cancelAllAppointments(absenceValue = 1, absenceUnit: 'day' | 'week' = 'day'): void {
    const idPersonnel = this.getCurrentPersonnelId();
    const date = this.selectedDate || this.getTodayLocalISO();

    if (!idPersonnel) {
      this.emergencyNotice = 'Utilisateur medical non identifie.';
      return;
    }

    const totalDays = absenceUnit === 'week'
      ? Math.max(1, absenceValue) * 7
      : Math.max(1, absenceValue);

    const dayDates = this.buildConsecutiveDates(date, totalDays);
    const requests = dayDates.map((dayDate) => this.rdvService.cancelAllMedicalStaffDay(idPersonnel, dayDate));

    this.loading = true;
    forkJoin(requests).pipe(finalize(() => { this.loading = false; })).subscribe({
      next: (responses) => {
        const totalCancelled = (responses || []).reduce((sum, resp) => {
          const count = Number(resp?.count || 0);
          return sum + (Number.isFinite(count) ? count : 0);
        }, 0);

        const label = absenceUnit === 'week' ? 'semaine(s)' : 'jour(s)';
        this.emergencyNotice = `Urgence medecin longue: absence de ${absenceValue} ${label}, ${totalCancelled} rendez-vous annules.`;
        this.notifications.info(this.emergencyNotice);
        this.loadDashboardData();
      },
      error: (err) => {
        this.emergencyNotice = this.getReadableHttpError(err, 'Erreur: Impossible d annuler les rendez-vous sur la periode.');
        this.notifications.error(this.emergencyNotice);
      }
    });
  }

  private buildConsecutiveDates(startDateIso: string, days: number): string[] {
    const safeDays = Math.max(1, Math.floor(days));
    const startDate = new Date(`${startDateIso}T00:00:00`);
    if (Number.isNaN(startDate.getTime())) {
      return [this.getTodayLocalISO()];
    }

    const result: string[] = [];
    for (let i = 0; i < safeDays; i += 1) {
      const current = new Date(startDate);
      current.setDate(startDate.getDate() + i);
      result.push(this.formatDateLocal(current));
    }

    return result;
  }

  private resolveEmergencyTargetAppointment(): {
    dayIndex: number;
    appointmentIndex: number;
    day: MedicalPlanningDay;
    appointment: MedicalPlanningAppointment;
  } | null {
    const selectedDay = this.selectedDate || this.getTodayLocalISO();
    const daysToInspect = this.weekPlanning.length > 0
      ? this.weekPlanning
      : [{ date: selectedDay, count: 0, appointments: this.todayPlanning || [] } as MedicalPlanningDay];

    const locateCandidateDay = (dayDate: string): { dayIndex: number; day: MedicalPlanningDay } | null => {
      const dayIndex = daysToInspect.findIndex((day) => (day.date || '').slice(0, 10) === dayDate);
      if (dayIndex === -1) {
        return null;
      }

      const day = daysToInspect[dayIndex];
      if ((day.appointments || []).length > 0) {
        return { dayIndex, day };
      }

      return null;
    };

    const preferredDay = locateCandidateDay(selectedDay);
    const fallbackDay = preferredDay
      || daysToInspect
        .map((day, dayIndex) => ({ dayIndex, day }))
        .find((entry) => (entry.day.appointments || []).length > 0)
      || null;

    if (!fallbackDay) {
      return null;
    }

    const dayIndex = fallbackDay.dayIndex;
    const day = fallbackDay.day;
    const appointments = day.appointments || [];

    const indexed = appointments
      .map((appointment, appointmentIndex) => ({ appointment, appointmentIndex }))
      .sort((a, b) => {
        const aStart = this.toMinutes((a.appointment.heureDebut || '').slice(0, 5));
        const bStart = this.toMinutes((b.appointment.heureDebut || '').slice(0, 5));
        return aStart - bStart;
      });

    const isCancelled = (value: MedicalPlanningAppointment): boolean => this.isCancelledStatus(value.statut);

    const candidates = indexed.filter((item) => !isCancelled(item.appointment));
    const usable = candidates.length > 0 ? candidates : indexed;
    if (usable.length === 0) {
      return null;
    }

    const currentDay = this.formatDateLocal(new Date());
    const effectiveDay = (day.date || '').slice(0, 10);
    if (effectiveDay !== currentDay) {
      const first = usable[0];
      return {
        dayIndex,
        appointmentIndex: first.appointmentIndex,
        day,
        appointment: first.appointment
      };
    }

    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    const active = usable.find((item) => {
      const start = this.toMinutes((item.appointment.heureDebut || '').slice(0, 5));
      const rawEnd = (item.appointment.heureFin || '').slice(0, 5);
      const end = rawEnd ? this.toMinutes(rawEnd) : start + 30;
      return currentMinutes >= start && currentMinutes < end;
    });

    if (active) {
      return {
        dayIndex,
        appointmentIndex: active.appointmentIndex,
        day,
        appointment: active.appointment
      };
    }

    const next = usable.find((item) => {
      const start = this.toMinutes((item.appointment.heureDebut || '').slice(0, 5));
      return start >= currentMinutes;
    });

    if (next) {
      return {
        dayIndex,
        appointmentIndex: next.appointmentIndex,
        day,
        appointment: next.appointment
      };
    }

    let closest = usable[0];
    let minDelta = Number.POSITIVE_INFINITY;
    for (const item of usable) {
      const start = this.toMinutes((item.appointment.heureDebut || '').slice(0, 5));
      const delta = Math.abs(start - currentMinutes);
      if (delta < minDelta) {
        minDelta = delta;
        closest = item;
      }
    }

    return {
      dayIndex,
      appointmentIndex: closest.appointmentIndex,
      day,
      appointment: closest.appointment
    };
  }

  private minutesToHour(totalMinutes: number): string {
    const normalized = Math.max(0, totalMinutes);
    const hh = Math.floor(normalized / 60)
      .toString()
      .padStart(2, '0');
    const mm = (normalized % 60).toString().padStart(2, '0');
    return `${hh}:${mm}`;
  }
}

import { Component, ChangeDetectorRef, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { Subscription, forkJoin, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';
import { AuthService } from 'src/app/services/auth.service';
import { AuthUser } from 'src/app/models/auth.model';
import {
  MedicalStaffPatientRecordResponse,
  MedicalPlanningAppointment,
  MedicalPlanningDay,
  RdvService
} from 'src/app/services/rdv.service';
import { EmergencyEventsService } from 'src/app/services/emergency-events.service';

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
  upcomingAppointments: Array<{ id: number; patientName: string; date: string; time: string; status: string }> = [];
  selectedAppointment: MedicalPlanningAppointment | null = null;
  patientRecord: MedicalStaffPatientRecordResponse | null = null;
  patientRecordLoading = false;
  patientRecordError = '';
  patientInConsultation = false;

  statistics = {
    todayAppointments: 0,
    patientsManaged: 0,
    pendingRequests: 0,
    completedToday: 0
  };

  emergencyNotice = '';
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
    this.emergencySub = this.emergencyEvents.emergency$.subscribe((type) => {
      if (type === 'patient-on-site') {
        this.delayCurrentAppointments(30);
        return;
      }

      if (type === 'doctor-left-short') {
        this.delayCurrentAppointments(60);
        return;
      }

      if (type === 'doctor-left-long') {
        this.cancelAllAppointments();
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

  private loadDashboardData(): void {
    const idPersonnel = this.currentUser?.id;
    if (!idPersonnel) {
      this.errorMessage = 'Utilisateur medical non identifie.';
      this.loading = false;
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.rdvService.getMedicalStaffPlanning(idPersonnel, this.selectedDate).subscribe({
      next: (planning) => {
        this.loading = false;
        this.weekStart = planning.weekStart || '';
        this.trackedWeekKey = this.weekStart || this.getWeekKey(this.selectedDate);
        this.todayPlanning = planning.todayPlanning || [];
        this.weekPlanning = planning.weekPlanning || [];
        this.applyMetrics();
      },
      error: (error) => {
        this.loading = false;
        console.error('Erreur chargement planning:', error);
        const errorMsg = error?.error?.error || 'Impossible de charger le planning du personnel de sante.';
        this.errorMessage = errorMsg;
      }
    });
  }

  private applyMetrics(): void {
    const today = this.selectedDate;
    const allWeekAppointments = this.weekPlanning.flatMap((day) => day.appointments || []);
    const uniquePatients = new Set<number>();

    allWeekAppointments.forEach((rdv) => {
      if (typeof rdv.idPatient === 'number') {
        uniquePatients.add(rdv.idPatient);
      }
    });

    const sorted = [...allWeekAppointments].sort((a, b) => {
      const aKey = `${a.dateRDV || ''} ${a.heureDebut || ''}`;
      const bKey = `${b.dateRDV || ''} ${b.heureDebut || ''}`;
      return aKey.localeCompare(bKey);
    });

    this.upcomingAppointments = sorted.slice(0, 6).map((rdv) => ({
      id: rdv.id,
      patientName: this.buildPatientName(rdv),
      date: rdv.dateRDV,
      time: (rdv.heureDebut || '').slice(0, 5),
      status: rdv.statut || 'En attente'
    }));

    this.statistics.todayAppointments = this.todayPlanning.length;
    this.statistics.patientsManaged = uniquePatients.size;
    this.statistics.pendingRequests = allWeekAppointments.filter((r) => (r.statut || '').toLowerCase().includes('attente')).length;
    this.statistics.completedToday = this.todayPlanning.filter((r) => {
      const isToday = (r.dateRDV || '').slice(0, 10) === today;
      const status = (r.statut || '').toLowerCase();
      const isDone = status.includes('confirm') || status.includes('termine');
      return isToday && isDone;
    }).length;
  }

  patientLabel(appointment: MedicalPlanningAppointment): string {
    return this.buildPatientName(appointment);
  }

  appointmentCin(appointment: MedicalPlanningAppointment): string {
    return this.getAppointmentCin(appointment) || '-';
  }

  appointmentEmail(appointment: MedicalPlanningAppointment): string {
    return this.getAppointmentEmail(appointment) || '-';
  }

  openAppointmentDetails(appointment: MedicalPlanningAppointment): void {
    const idPatient = appointment.idPatient;
    const idPersonnel = this.currentUser?.id;

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

    this.rdvService
      .getMedicalStaffPatientRecord(idPersonnel, idPatient, appointment.id)
      .pipe(finalize(() => {
        this.patientRecordLoading = false;
      }))
      .subscribe({
        next: (record) => {
          this.patientRecord = record;
        },
        error: () => {
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

  private delayCurrentAppointments(delayMinutes: number): void {
    const target = this.resolveEmergencyTargetAppointment();
    if (!target) {
      this.emergencyNotice = 'Aucun rendez-vous à décaler pour cette journée.';
      return;
    }

    const { dayIndex, day, appointment } = target;
    const targetHour = (appointment.heureDebut || '').slice(0, 2);
    const updatedAppointments = [...(day.appointments || [])];
    const shiftedAppointments: MedicalPlanningAppointment[] = [];

    for (let index = 0; index < updatedAppointments.length; index += 1) {
      const current = updatedAppointments[index];
      const currentHour = (current.heureDebut || '').slice(0, 2);
      const isCancelled = (current.statut || '').toLowerCase().includes('annule');
      if (isCancelled || currentHour !== targetHour) {
        continue;
      }

      const start = this.toMinutes((current.heureDebut || '').slice(0, 5));
      const rawEnd = (current.heureFin || '').slice(0, 5);
      const end = rawEnd ? this.toMinutes(rawEnd) : start + 30;

      const shiftedAppointment: MedicalPlanningAppointment = {
        ...current,
        heureDebut: this.minutesToHour(start + delayMinutes),
        heureFin: this.minutesToHour(end + delayMinutes),
        motifConsultation: current.motifConsultation || 'consultation',
        statut: 'Décalé (urgence patient)'
      };

      updatedAppointments[index] = shiftedAppointment;
      shiftedAppointments.push(shiftedAppointment);
    }

    if (shiftedAppointments.length === 0) {
      this.emergencyNotice = 'Aucun rendez-vous actif a decaler pour cette heure.';
      return;
    }

    this.weekPlanning = this.weekPlanning.map((day, idx) => {
      if (idx === dayIndex) {
        return {
          ...day,
          appointments: updatedAppointments,
          count: updatedAppointments.length
        };
      }
      return day;
    });

    this.todayPlanning = [...updatedAppointments];
    if (this.selectedAppointment) {
      const updatedSelected = updatedAppointments.find((item) => item.id === this.selectedAppointment?.id);
      if (updatedSelected) {
        this.selectedAppointment = updatedSelected;
      }
    }
    this.applyMetrics();
    this.changeDetector.markForCheck();
    this.emergencyNotice = `Urgence patient: ${shiftedAppointments.length} rendez-vous de ${targetHour}h ont ete decales de ${delayMinutes} minutes.`;

    // Persist all shifted appointments to database.
    const persistRequests = shiftedAppointments.map((item) => {
      const updatePayload = {
        id: item.id,
        idPatient: item.idPatient,
        idPersonnel: item.idPersonnel,
        dateRDV: item.dateRDV,
        heureDebut: item.heureDebut,
        heureFin: item.heureFin,
        motifConsultation: item.motifConsultation || 'consultation',
        statut: item.statut
      };

      return this.rdvService.updateRdv(updatePayload).pipe(catchError(() => of(null)));
    });

    forkJoin(persistRequests).subscribe({
      next: (results) => {
        const failed = results.filter((result) => result === null).length;
        if (failed > 0) {
          this.emergencyNotice = `Urgence patient appliquee partiellement: ${shiftedAppointments.length - failed}/${shiftedAppointments.length} rendez-vous sauvegardes.`;
        }
      },
      error: () => {
        this.emergencyNotice = `Erreur: Les changements n'ont pas pu etre sauvegardes.`;
      }
    });
  }

  private cancelAllAppointments(): void {
    const target = this.resolveEmergencyTargetAppointment();
    if (!target) {
      this.emergencyNotice = 'Urgence medecin: aucun rendez-vous a annuler.';
      return;
    }

    const { dayIndex, appointmentIndex, day, appointment } = target;
    const motif = (appointment.motifConsultation || '').trim();
    const hasCancelledPrefix = motif.toLowerCase().startsWith('annule');
    const updatedAppointment = {
      ...appointment,
      statut: 'Annule (urgence medecin)',
      motifConsultation: hasCancelledPrefix ? motif : `Annule - ${motif || 'consultation'}`
    };

    const updatedAppointments = [...(day.appointments || [])];
    updatedAppointments[appointmentIndex] = updatedAppointment;

    this.weekPlanning = this.weekPlanning.map((day) => {
      if ((day.date || '').slice(0, 10) === (this.selectedDate || this.getTodayLocalISO())) {
        return {
          ...day,
          appointments: updatedAppointments,
          count: updatedAppointments.length
        };
      }

      return day;
    });

    this.todayPlanning = [...updatedAppointments];
    if (this.selectedAppointment?.id === updatedAppointment.id) {
      this.selectedAppointment = updatedAppointment;
    }
    this.applyMetrics();

    // Force Angular to detect changes
    this.changeDetector.markForCheck();
    this.emergencyNotice = 'Urgence medecin: le rendez-vous a ete annule.';

    // Persist to database
    this.rdvService.updateRdv(updatedAppointment).subscribe({
      next: () => {
        // Success message is already set above
      },
      error: () => {
        this.emergencyNotice = `Erreur: Les changements n'ont pas pu être sauvegardés.`;
      }
    });
  }

  private resolveEmergencyTargetAppointment(): {
    dayIndex: number;
    appointmentIndex: number;
    day: MedicalPlanningDay;
    appointment: MedicalPlanningAppointment;
  } | null {
    const selectedDay = this.selectedDate || this.getTodayLocalISO();
    const dayIndex = this.weekPlanning.findIndex((day) => (day.date || '').slice(0, 10) === selectedDay);

    if (dayIndex === -1) {
      return null;
    }

    const day = this.weekPlanning[dayIndex];
    const appointments = day.appointments || [];
    if (appointments.length === 0) {
      return null;
    }

    const indexed = appointments
      .map((appointment, appointmentIndex) => ({ appointment, appointmentIndex }))
      .sort((a, b) => {
        const aStart = this.toMinutes((a.appointment.heureDebut || '').slice(0, 5));
        const bStart = this.toMinutes((b.appointment.heureDebut || '').slice(0, 5));
        return aStart - bStart;
      });

    const isCancelled = (value: MedicalPlanningAppointment): boolean =>
      (value.statut || '').toLowerCase().includes('annule');

    const candidates = indexed.filter((item) => !isCancelled(item.appointment));
    const usable = candidates.length > 0 ? candidates : indexed;
    if (usable.length === 0) {
      return null;
    }

    const currentDay = this.formatDateLocal(new Date());
    if (selectedDay !== currentDay) {
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

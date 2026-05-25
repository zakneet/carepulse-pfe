import { Component, OnInit } from '@angular/core';
import { CalendarOptions, EventClickArg, EventInput } from '@fullcalendar/core';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { Router } from '@angular/router';
import {
  OptimizePatient,
  OptimizeRequest,
  OptimizeResponse,
  OptimizedAppointment,
  RdvService,
} from '../services/rdv.service';

interface AppointmentProfile {
  patientId: number;
  nomComplet: string;
  telephone: string;
  cin: string;
  motif: string;
  availability: string;
  appointmentStart: string;
  appointmentEnd: string;
  durationMinutes: number;
  isActive: boolean;
}

@Component({
  selector: 'app-optimized-calendar',
  templateUrl: './optimized-calendar.component.html',
  styleUrls: ['./optimized-calendar.component.css'],
})
export class OptimizedCalendarComponent implements OnInit {
  isLoading = false;
  errorMessage = '';
  noSolutionMessage = '';
  selectedDate = this.getTodayIsoDate();
  selectedProfile: AppointmentProfile | null = null;
  private latestAppointments: OptimizedAppointment[] = [];
  private patientSwitchState: Record<number, boolean> = {};

  readonly optimizePayload: OptimizeRequest = {
    patients: [
      { id: 1, nom: 'Benali', prenom: 'Youssef', telephone: '0611223344', cin: 'AB12345', motif: 'Consultation', start: 480, end: 660, duration: 30 },
      { id: 2, nom: 'Alaoui', prenom: 'Sara', telephone: '0622334455', cin: 'BC23456', motif: 'Controle', start: 510, end: 690, duration: 30 },
      { id: 3, nom: 'Rami', prenom: 'Ilyas', telephone: '0633445566', cin: 'CD34567', motif: 'Suivi urgent', start: 540, end: 720, duration: 30, priority: 1000, isUrgent: true },
      { id: 4, nom: 'Kabbaj', prenom: 'Nour', telephone: '0644556677', cin: 'DE45678', motif: 'Bilan', start: 570, end: 750, duration: 30 },
      { id: 5, nom: 'Saidi', prenom: 'Imane', telephone: '0655667788', cin: 'EF56789', motif: 'Consultation', start: 600, end: 780, duration: 30 },
      { id: 6, nom: 'Tazi', prenom: 'Mehdi', telephone: '0666778899', cin: 'FG67890', motif: 'Controle', start: 630, end: 810, duration: 30 },
      { id: 7, nom: 'Boukili', prenom: 'Lina', telephone: '0677889900', cin: 'GH78901', motif: 'Avis medical', start: 660, end: 870, duration: 30 },
      { id: 8, nom: 'Chraibi', prenom: 'Adam', telephone: '0688990011', cin: 'HI89012', motif: 'Consultation', start: 690, end: 900, duration: 30 },
      { id: 9, nom: 'Sefrioui', prenom: 'Maya', telephone: '0699001122', cin: 'IJ90123', motif: 'Suivi', start: 720, end: 960, duration: 30 },
      { id: 10, nom: 'Idrissi', prenom: 'Omar', telephone: '0600112233', cin: 'JK01234', motif: 'Controle', start: 750, end: 1020, duration: 30 },
    ],
    doctor_schedule: { start: 480, end: 1080 },
  };

  calendarOptions: CalendarOptions = {
    plugins: [timeGridPlugin, interactionPlugin],
    initialView: 'timeGridDay',
    allDaySlot: false,
    nowIndicator: true,
    slotMinTime: '08:00:00',
    slotMaxTime: '18:00:00',
    height: 'auto',
    headerToolbar: {
      left: 'title',
      center: '',
      right: 'today prev,next',
    },
    events: [],
    eventClick: this.handleEventClick.bind(this),
  };

  constructor(
    private readonly rdvService: RdvService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.loadOptimizedSchedule();
  }

  reloadSchedule(): void {
    this.loadOptimizedSchedule();
  }

  private loadOptimizedSchedule(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.noSolutionMessage = '';

    this.rdvService.optimizeSchedule(this.optimizePayload).subscribe({
      next: (response: OptimizeResponse) => {
        this.isLoading = false;
        if (response.status !== 'success') {
          this.errorMessage = response.message || 'Erreur pendant l\'optimisation.';
          this.calendarOptions = { ...this.calendarOptions, events: [] };
          return;
        }

        const appointments = Array.isArray(response.data) ? response.data : [];
        if (appointments.length === 0) {
          this.noSolutionMessage = 'Aucune solution trouvée pour ces contraintes.';
          this.calendarOptions = { ...this.calendarOptions, events: [] };
          return;
        }

        this.latestAppointments = appointments;
        this.refreshCalendarEvents();
      },
      error: (error: unknown) => {
        this.isLoading = false;
        const defaultMessage = 'Impossible de charger le planning optimisé.';
        const candidate = (error as { error?: { message?: string } })?.error?.message;
        this.errorMessage = typeof candidate === 'string' && candidate.trim() ? candidate : defaultMessage;
        this.calendarOptions = { ...this.calendarOptions, events: [] };
      },
    });
  }

  private mapAppointmentsToEvents(appointments: OptimizedAppointment[]): EventInput[] {
    return appointments.map((appointment, index) => {
      const palette = [
        { bg: '#0b7285', border: '#0b7285' },
        { bg: '#1f9d8a', border: '#1f9d8a' },
        { bg: '#f97316', border: '#f97316' },
      ];
      const color = palette[index % palette.length];
      const isActive = this.getPatientSwitchState(appointment.patient_id);

      return {
        id: String(appointment.patient_id),
        title: this.getEventTitle(appointment.patient_id),
        start: this.minutesToIsoDateTime(appointment.start, this.selectedDate),
        end: this.minutesToIsoDateTime(appointment.end, this.selectedDate),
        backgroundColor: isActive ? color.bg : '#94a3b8',
        borderColor: isActive ? color.border : '#94a3b8',
        textColor: '#ffffff',
        extendedProps: {
          patientId: appointment.patient_id,
          startMinutes: appointment.start,
          endMinutes: appointment.end,
          isActive,
        },
      };
    });
  }

  togglePatientStatus(): void {
    if (!this.selectedProfile) {
      return;
    }

    const patientId = this.selectedProfile.patientId;
    const nextState = !this.getPatientSwitchState(patientId);
    this.patientSwitchState[patientId] = nextState;
    this.selectedProfile = { ...this.selectedProfile, isActive: nextState };
    this.refreshCalendarEvents();
  }

  goToPatientProfile(): void {
    if (!this.selectedProfile) {
      return;
    }

    this.router.navigate(['/medical-staff/doctor/patient-profile', this.selectedProfile.patientId]);
    this.closeProfilePopup();
  }

  closeProfilePopup(): void {
    this.selectedProfile = null;
  }

  private minutesToIsoDateTime(minutes: number, dateIso: string): string {
    const total = Number.isFinite(minutes) ? Math.max(0, Math.floor(minutes)) : 0;
    const hours = Math.floor(total / 60);
    const mins = total % 60;
    const hh = String(hours).padStart(2, '0');
    const mm = String(mins).padStart(2, '0');
    return `${dateIso}T${hh}:${mm}:00`;
  }

  private getTodayIsoDate(): string {
    return new Date().toISOString().slice(0, 10);
  }

  private handleEventClick(clickInfo: EventClickArg): void {
    const patientId = Number(clickInfo.event.extendedProps['patientId']);
    const patient = this.findPatientById(patientId);

    if (!patient) {
      return;
    }

    const startMinutes = Number(clickInfo.event.extendedProps['startMinutes']);
    const endMinutes = Number(clickInfo.event.extendedProps['endMinutes']);
    this.selectedProfile = {
      patientId,
      nomComplet: `${patient.prenom || ''} ${patient.nom || ''}`.trim() || `Patient ${patientId}`,
      telephone: patient.telephone || '-',
      cin: patient.cin || '-',
      motif: patient.motif || 'Consultation',
      availability: `${this.minutesToDisplayTime(patient.start)} - ${this.minutesToDisplayTime(patient.end)}`,
      appointmentStart: this.minutesToDisplayTime(startMinutes),
      appointmentEnd: this.minutesToDisplayTime(endMinutes),
      durationMinutes: Math.max(0, endMinutes - startMinutes),
      isActive: this.getPatientSwitchState(patientId),
    };
  }

  private refreshCalendarEvents(): void {
    const events = this.mapAppointmentsToEvents(this.latestAppointments);
    this.calendarOptions = {
      ...this.calendarOptions,
      initialDate: this.selectedDate,
      events,
    };
  }

  private getPatientSwitchState(patientId: number): boolean {
    if (typeof this.patientSwitchState[patientId] === 'boolean') {
      return this.patientSwitchState[patientId];
    }
    this.patientSwitchState[patientId] = true;
    return true;
  }

  private minutesToDisplayTime(minutes: number): string {
    const total = Number.isFinite(minutes) ? Math.max(0, Math.floor(minutes)) : 0;
    const hours = Math.floor(total / 60);
    const mins = total % 60;
    return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
  }

  private findPatientById(patientId: number): OptimizePatient | undefined {
    return this.optimizePayload.patients.find((patient) => patient.id === patientId);
  }

  private getEventTitle(patientId: number): string {
    const patient = this.findPatientById(patientId);
    if (!patient) {
      return `Patient ${patientId}`;
    }

    if (patient.prenom || patient.nom) {
      return `${patient.prenom || ''} ${patient.nom || ''}`.trim();
    }

    return `Patient ${patientId}`;
  }
}

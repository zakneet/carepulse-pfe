import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { HistoryFilterOption } from '../../patient-dashboard.models';

type AppointmentSource = {
  id: number;
  dateRDV?: string;
  heureDebut?: string;
  heureFin?: string;
  motifConsultation?: string;
  statut?: string;
  medecin?: string;
  medecinNom?: string;
  medecinPrenom?: string;
  specialite?: string;
  dateLabel?: string;
  timeLabel?: string;
  doctorLabel?: string;
  tone?: string;
};

type AppointmentRow = {
  dateLabel: string;
  timeLabel: string;
  doctorLabel: string;
  tone: string;
  id: number;
  motifConsultation?: string;
  statut?: string;
};

@Component({
  selector: 'app-appointment-history',
  templateUrl: './appointment-history.component.html',
  styleUrls: ['./appointment-history.component.scss']
})
export class AppointmentHistoryComponent implements OnChanges {
  @Input() appointments: AppointmentSource[] = [];

  filters: HistoryFilterOption[] = [
    { value: 'all', label: 'Tous' },
    { value: 'scheduled', label: 'Planifiés' },
    { value: 'done', label: 'Terminés' },
    { value: 'cancelled', label: 'Annulés' },
    { value: 'delayed', label: 'Reportés' },
  ];

  selectedFilter: HistoryFilterOption['value'] = 'all';
  searchTerm = '';
  rows: AppointmentRow[] = [];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.appointments) {
      this.rows = (this.appointments || []).map((appointment) => this.mapAppointment(appointment));
    }
  }

  get filteredRows(): AppointmentRow[] {
    const term = this.searchTerm.trim().toLowerCase();
    return this.rows.filter((row) => {
      const matchesFilter = this.selectedFilter === 'all' || row.tone === this.selectedFilter;
      const haystack = `${row.doctorLabel} ${row.motifConsultation || ''} ${row.statut || ''}`.toLowerCase();
      const matchesSearch = !term || haystack.includes(term);
      return matchesFilter && matchesSearch;
    });
  }

  setFilter(filter: HistoryFilterOption['value']): void {
    this.selectedFilter = filter;
  }

  trackById(_: number, row: AppointmentRow): number {
    return row.id;
  }

  private mapAppointment(appointment: AppointmentSource): AppointmentRow {
    return {
      id: appointment.id,
      dateLabel: appointment.dateLabel || this.formatDate(appointment.dateRDV || ''),
      timeLabel: appointment.timeLabel || this.formatTimeRange(appointment.heureDebut, appointment.heureFin),
      doctorLabel: appointment.doctorLabel || this.buildDoctorLabel(appointment),
      tone: appointment.tone || this.getTone(appointment.statut),
      motifConsultation: appointment.motifConsultation,
      statut: appointment.statut,
    };
  }

  private buildDoctorLabel(appointment: AppointmentSource): string {
    if (appointment.medecin && appointment.medecin.trim()) {
      return appointment.medecin.trim();
    }

    const fullName = `${(appointment.medecinPrenom || '').trim()} ${(appointment.medecinNom || '').trim()}`.trim();
    return fullName || 'Médecin';
  }

  private formatDate(dateValue: string): string {
    const parsed = new Date(`${dateValue.slice(0, 10)}T00:00:00`);
    return Number.isNaN(parsed.getTime()) ? '-' : parsed.toLocaleDateString('fr-FR');
  }

  private formatTimeRange(start?: string, end?: string): string {
    const startLabel = (start || '').slice(0, 5);
    const endLabel = (end || '').slice(0, 5);
    return startLabel && endLabel ? `${startLabel} - ${endLabel}` : startLabel || endLabel || '-';
  }

  private getTone(status?: string): string {
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
}

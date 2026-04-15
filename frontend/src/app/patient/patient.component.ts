import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Rdv, RdvService } from '../services/rdv.service';

type ConsultationItem = {
  id: number;
  medecin: string;
  dateLabel: string;
  heureLabel: string;
  motif: string;
  statut: string;
};

@Component({
  selector: 'app-patient',
  templateUrl: './patient.component.html',
  styleUrls: ['./patient.component.css']
})
export class PatientComponent implements OnInit {
  consultations: ConsultationItem[] = [];
  errorMessage = '';
  isLoading = true;

  constructor(
    private authService: AuthService,
    private rdvService: RdvService
  ) {}

  ngOnInit(): void {
    this.loadConsultationsDone();
  }

  private loadConsultationsDone(): void {
    const patientId = this.getPatientId();
    if (!patientId) {
      this.isLoading = false;
      this.errorMessage = 'Patient non authentifie.';
      return;
    }

    this.rdvService.getRdvs().subscribe({
      next: (rdvs) => {
        this.errorMessage = '';
        this.consultations = rdvs
          .filter((rdv) => rdv.idPatient === patientId)
          .filter((rdv) => this.isConsultationDone(rdv))
          .sort((a, b) => {
            const ad = this.toDateTime(a.dateRDV, a.heureFin || a.heureDebut)?.getTime() || 0;
            const bd = this.toDateTime(b.dateRDV, b.heureFin || b.heureDebut)?.getTime() || 0;
            return bd - ad;
          })
          .map((rdv) => ({
            id: rdv.id,
            medecin: this.buildMedecinName(rdv),
            dateLabel: this.formatDate(rdv.dateRDV),
            heureLabel: this.formatHeureLabel(rdv),
            motif: rdv.motifConsultation || '-',
            statut: rdv.statut || 'Termine'
          }));

        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Impossible de charger les consultations.';
      }
    });
  }

  private getPatientId(): number | null {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser?.id) {
      return currentUser.id;
    }

    const storedUserRaw = localStorage.getItem('authUser');
    if (!storedUserRaw) {
      return null;
    }

    try {
      const storedUser = JSON.parse(storedUserRaw) as { id?: number };
      return typeof storedUser.id === 'number' ? storedUser.id : null;
    } catch {
      return null;
    }
  }

  private isConsultationDone(rdv: Rdv): boolean {
    const statut = (rdv.statut || '').trim().toLowerCase();
    const completedStatuses = ['termine', 'terminee', 'effectue', 'effectuee', 'realise', 'realisee', 'done', 'completed'];

    if (completedStatuses.includes(statut)) {
      return true;
    }

    const endDate = this.toDateTime(rdv.dateRDV, rdv.heureFin || rdv.heureDebut);
    if (!endDate) {
      return false;
    }

    return endDate.getTime() < Date.now();
  }

  private toDateTime(dateValue: string, timeValue?: string): Date | null {
    if (!dateValue) {
      return null;
    }

    const datePart = dateValue.includes('T') ? dateValue.split('T')[0] : dateValue;
    const timePart = (timeValue || '00:00:00').slice(0, 8);
    const composed = `${datePart}T${timePart}`;
    const parsed = new Date(composed);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  private buildMedecinName(rdv: Rdv): string {
    const prenom = (rdv.personnelPrenom || '').trim();
    const nom = (rdv.personnelNom || '').trim();
    const fullName = `${prenom} ${nom}`.trim();

    if (fullName) {
      return fullName;
    }

    if (typeof rdv.idPersonnel === 'number') {
      return `Medecin #${rdv.idPersonnel}`;
    }

    return 'Medecin non renseigne';
  }

  private formatDate(dateValue: string): string {
    const parsed = this.toDateTime(dateValue, '00:00:00');
    if (!parsed) {
      return '-';
    }

    return parsed.toLocaleDateString('fr-FR');
  }

  private formatHeureLabel(rdv: Rdv): string {
    const start = (rdv.heureDebut || '').slice(0, 5);
    const end = (rdv.heureFin || '').slice(0, 5);

    if (start && end) {
      return `${start} - ${end}`;
    }

    return start || end || '-';
  }
}

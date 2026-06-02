import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { RdvService, MedicalStaffPatientListItem } from 'src/app/services/rdv.service';

interface EnrichedPatient extends MedicalStaffPatientListItem {
  condition?: string;
  lastVisit?: string;
  nextVisit?: string;
  risk?: 'LOW' | 'MODERATE' | 'HIGH';
}

@Component({
  selector: 'app-medical-staff-patients',
  templateUrl: './medical-staff-patients.component.html',
  styleUrls: ['./medical-staff-patients.component.css']
})
export class MedicalStaffPatientsComponent {
  staffView: 'doctor' | 'nurse' = 'doctor';
  baseRoute = '/medical-staff/doctor';
  loading = false;
  errorMessage = '';
  patients: EnrichedPatient[] = [];
  searchTerm = '';
  newThisMonth = 0;

  private readonly avatarColors = [
    'linear-gradient(135deg,#0284c7,#38bdf8)',
    'linear-gradient(135deg,#7c3aed,#a78bfa)',
    'linear-gradient(135deg,#059669,#34d399)',
    'linear-gradient(135deg,#d97706,#fbbf24)',
    'linear-gradient(135deg,#dc2626,#f87171)',
    'linear-gradient(135deg,#0891b2,#22d3ee)',
    'linear-gradient(135deg,#7c3aed,#c4b5fd)',
    'linear-gradient(135deg,#047857,#6ee7b7)',
  ];

  constructor(
    private rdvService: RdvService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.staffView = this.route.snapshot.data['staffView'] === 'nurse' ? 'nurse' : 'doctor';
    this.baseRoute = this.staffView === 'nurse' ? '/medical-staff/nurse' : '/medical-staff/doctor';
    this.loadPatients();
  }

  private loadPatients(): void {
    const idPersonnel = this.getPersonnelId();
    if (!idPersonnel) {
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.rdvService.getMedicalStaffPatients(idPersonnel).subscribe({
      next: (rows) => {
        this.loading = false;
        this.patients = (rows || []).map((p) => ({
          ...p,
          lastVisit: this.formatDate(p.lastVisit),
          nextVisit: this.formatDate(p.nextVisit),
          condition: p.condition || 'Consultation',
          risk: p.risk || 'LOW'
        }));
        this.newThisMonth = this.patients.filter((p) => p.newThisMonth).length;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger la liste des patients.';
      }
    });
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; idPersonnel?: number; id_personnel?: number } | null;
    return user?.id ?? user?.idPersonnel ?? user?.id_personnel;
  }

  private formatDate(value?: string | null): string | undefined {
    if (!value) return undefined;
    const d = new Date(`${value}T00:00:00`);
    if (Number.isNaN(d.getTime())) return undefined;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  get filteredPatients(): EnrichedPatient[] {
    const query = this.searchTerm.trim().toLowerCase();
    if (!query) return this.patients;
    return this.patients.filter((p) =>
      [p.nom, p.prenom, p.email || '', p.telephone || '', String(p.id), p.condition || '']
        .join(' ').toLowerCase().includes(query)
    );
  }

  onSearchTermChange(event: Event): void {
    const target = event.target as HTMLInputElement | null;
    this.searchTerm = target?.value ?? '';
  }

  openPatientProfile(patientId: number): void {
    this.router.navigate([this.baseRoute, 'patient-profile', patientId]);
  }

  getAvatarColor(index: number): string {
    return this.avatarColors[index % this.avatarColors.length];
  }

  getAge(patient: EnrichedPatient): number {
    return 25 + (patient.id % 45);
  }

  getRiskClass(risk: string | undefined): string {
    switch ((risk || 'LOW').toUpperCase()) {
      case 'HIGH': return 'pts-risk-badge--high';
      case 'MODERATE': return 'pts-risk-badge--moderate';
      default: return 'pts-risk-badge--low';
    }
  }
}

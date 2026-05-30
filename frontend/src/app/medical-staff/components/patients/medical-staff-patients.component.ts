import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { RdvService, MedicalStaffPatientListItem } from 'src/app/services/rdv.service';

// Enriched patient type with UI fields
interface EnrichedPatient extends MedicalStaffPatientListItem {
  condition?: string;
  lastVisit?: string;
  nextVisit?: string;
  risk?: 'LOW' | 'MODERATE' | 'HIGH';
  dateNaissance?: string;
}

// Static enrichment data keyed by patient index (cycles if list is longer)
const CONDITIONS = [
  'Hypertension', 'Coronary artery disease', 'Annual check-up',
  'Arrhythmia follow-up', 'Post-stent monitoring', 'Palpitations',
  'ECG review', 'First consultation', 'Diabetes type 2', 'Asthma'
];
const RISKS: Array<'LOW' | 'MODERATE' | 'HIGH'> = ['LOW', 'HIGH', 'LOW', 'MODERATE', 'MODERATE', 'HIGH', 'LOW', 'LOW', 'HIGH', 'MODERATE'];

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
    const currentUser = this.authService.getCurrentUser() as unknown as {
      id?: number;
      idPersonnel?: number;
      id_personnel?: number;
    } | null;
    const idPersonnel = currentUser?.id ?? currentUser?.idPersonnel ?? currentUser?.id_personnel;
    if (!idPersonnel) {
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.rdvService.getMedicalStaffPatients(idPersonnel).subscribe({
      next: (rdvs) => {
        this.loading = false;
        // Enrich with static UI data
        this.patients = (rdvs || []).map((p, i) => ({
          ...p,
          condition: CONDITIONS[i % CONDITIONS.length],
          lastVisit: this.mockDate(-((i * 7) + 3)),
          nextVisit: i % 5 !== 3 ? this.mockDate((i * 5) + 2) : undefined,
          risk: RISKS[i % RISKS.length]
        } as EnrichedPatient));
        this.newThisMonth = Math.floor(this.patients.length * 0.017) || 38;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger la liste des patients.';
      }
    });
  }

  private mockDate(offsetDays: number): string {
    const d = new Date();
    d.setDate(d.getDate() + offsetDays);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  get filteredPatients(): EnrichedPatient[] {
    const query = this.searchTerm.trim().toLowerCase();
    if (!query) return this.patients;
    return this.patients.filter(p =>
      [p.nom, p.prenom, p.email || '', p.telephone || '', String(p.id)]
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
    // Generate a plausible age from patient id
    return 25 + (patient.id % 45);
  }

  getRiskClass(risk: string | undefined): string {
    switch ((risk || 'LOW').toUpperCase()) {
      case 'HIGH':     return 'pts-risk-badge--high';
      case 'MODERATE': return 'pts-risk-badge--moderate';
      default:         return 'pts-risk-badge--low';
    }
  }
}

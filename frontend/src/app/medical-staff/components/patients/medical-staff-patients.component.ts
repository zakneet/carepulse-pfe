import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { RdvService, MedicalStaffPatientListItem } from 'src/app/services/rdv.service';

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
  patients: MedicalStaffPatientListItem[] = [];
  searchTerm = '';

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
        this.patients = rdvs || [];
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger la liste des patients.';
      }
    });
  }

  get filteredPatients(): MedicalStaffPatientListItem[] {
    const query = this.searchTerm.trim().toLowerCase();
    if (!query) {
      return this.patients;
    }

    return this.patients.filter((patient) => {
      const searchableText = [
        patient.nom,
        patient.prenom,
        patient.email || '',
        patient.telephone || '',
        String(patient.id),
        String(patient.rdvCount)
      ]
        .join(' ')
        .toLowerCase();

      return searchableText.includes(query);
    });
  }

  onSearchTermChange(event: Event): void {
    const target = event.target as HTMLInputElement | null;
    this.searchTerm = target?.value ?? '';
  }

  openPatientProfile(patientId: number): void {
    this.router.navigate([this.baseRoute, 'patient-profile', patientId]);
  }
}

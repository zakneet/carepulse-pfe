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
    const idPersonnel = this.authService.getCurrentUser()?.id;
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

  openPatientProfile(patientId: number): void {
    this.router.navigate([this.baseRoute, 'patient-profile', patientId]);
  }
}

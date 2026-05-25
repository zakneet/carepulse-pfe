import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {
  RdvService,
  MedicalStaffPatientFullProfileResponse
} from 'src/app/services/rdv.service';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-medical-staff-patient-profile',
  templateUrl: './medical-staff-patient-profile.component.html',
  styleUrls: ['./medical-staff-patient-profile.component.css']
})
export class MedicalStaffPatientProfileComponent implements OnInit {
  staffView: 'doctor' | 'nurse' = 'doctor';
  baseRoute = '/medical-staff/doctor';
  canEdit = false;
  isEditMode = false;
  saving = false;
  loading = true;
  errorMessage = '';
  successMessage = '';
  profileData: MedicalStaffPatientFullProfileResponse | null = null;
  patientId: number = 0;
  editForm = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    cin: '',
    sexe: '',
    dateNaissance: '',
    allergies: '',
    maladies: ''
  };

  constructor(
    private route: ActivatedRoute,
    private authService: AuthService,
    private rdvService: RdvService
  ) {}

  ngOnInit(): void {
    this.staffView = this.route.snapshot.data['staffView'] === 'nurse' ? 'nurse' : 'doctor';
    this.baseRoute = this.staffView === 'nurse' ? '/medical-staff/nurse' : '/medical-staff/doctor';
    this.canEdit = this.route.snapshot.data['profileEditable'] === true;

    this.route.params.subscribe(params => {
      this.patientId = params['idPatient'] || Number(this.route.snapshot.queryParamMap.get('idPatient'));
      if (this.patientId) {
        this.loadPatientProfile();
      }
    });
  }

  loadPatientProfile(clearMessages = true): void {
    this.loading = true;
    if (clearMessages) {
      this.errorMessage = '';
      this.successMessage = '';
    }

    const currentUser = this.authService.getCurrentUser() as unknown as {
      id?: number;
      idPersonnel?: number;
      id_personnel?: number;
    } | null;
    const idPersonnel = currentUser?.id ?? currentUser?.idPersonnel ?? currentUser?.id_personnel;

    if (!idPersonnel) {
      this.errorMessage = 'Utilisateur non identifié';
      this.loading = false;
      return;
    }

    this.rdvService.getMedicalStaffPatientFullProfile(idPersonnel, this.patientId).subscribe({
      next: (data: MedicalStaffPatientFullProfileResponse) => {
        this.profileData = data;
        this.patchEditForm(data);
        this.loading = false;
      },
      error: (err: any) => {
        this.errorMessage = 'Impossible de charger le profil du patient';
        this.loading = false;
        console.error('Error loading patient profile:', err);
      }
    });
  }

  formatShortDate(value: string | null | undefined): string {
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

  saveProfile(): void {
    if (!this.canEdit || !this.isEditMode || !this.profileData) {
      return;
    }

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

    this.saving = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.rdvService.updateMedicalStaffPatientFullProfile({
      idPersonnel,
      idPatient: this.patientId,
      patient: {
        nom: this.editForm.nom,
        prenom: this.editForm.prenom,
        email: this.editForm.email || null,
        telephone: this.editForm.telephone || null,
        cin: this.editForm.cin || null,
        sexe: this.editForm.sexe || null,
        dateNaissance: this.editForm.dateNaissance || null,
        allergies: this.parseCommaValues(this.editForm.allergies),
        maladies: this.parseCommaValues(this.editForm.maladies)
      }
    }).subscribe({
      next: () => {
        this.saving = false;
        this.isEditMode = false;
        this.successMessage = 'Profil patient mis a jour.';
        this.loadPatientProfile(false);
      },
      error: (error) => {
        this.saving = false;
        this.errorMessage = error?.error?.error || 'Impossible de mettre a jour le profil patient.';
      }
    });
  }

  private patchEditForm(data: MedicalStaffPatientFullProfileResponse): void {
    this.editForm = {
      nom: data.patient.nom || '',
      prenom: data.patient.prenom || '',
      email: data.patient.email || '',
      telephone: data.patient.telephone || '',
      cin: data.patient.cin || '',
      sexe: data.patient.sexe || '',
      dateNaissance: data.patient.dateNaissance || '',
      allergies: (data.patient.allergies || []).join(', '),
      maladies: (data.patient.maladies || []).join(', ')
    };
  }

  private parseCommaValues(value: string): string[] {
    return (value || '')
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  }

  toggleEditMode(): void {
    if (!this.canEdit) {
      return;
    }

    this.isEditMode = !this.isEditMode;
    this.successMessage = '';

    // Reset form values when leaving edit mode to avoid stale unsaved values.
    if (!this.isEditMode && this.profileData) {
      this.patchEditForm(this.profileData);
    }
  }
}

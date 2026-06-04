import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { RdvService } from 'src/app/services/rdv.service';

@Component({
  selector: 'app-medical-staff-form',
  templateUrl: './medical-staff-form.component.html',
  styleUrls: ['./medical-staff-form.component.css']
})
export class MedicalStaffFormComponent implements OnInit {
  staffView: 'doctor' | 'nurse' = 'doctor';
  baseRoute = '/medical-staff/doctor';
  isEmergencyMode = false;
  emergencySource = '';
  searchCin = '';
  searchMessage = '';
  searching = false;
  saving = false;
  saveMessage = '';
  saveError = '';

  patientForm = {
    nom: '',
    prenom: '',
    cin: '',
    telephone: '',
    email: '',
    agePatient: '',
    dateRDV: '',
    heureDebut: '',
    motifConsultation: 'consultation'
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private rdvService: RdvService
  ) {}

  ngOnInit(): void {
    this.staffView = this.route.snapshot.data['staffView'] === 'nurse' ? 'nurse' : 'doctor';
    this.baseRoute = this.staffView === 'nurse' ? '/medical-staff/nurse' : '/medical-staff/doctor';
    const mode = (this.route.snapshot.queryParamMap.get('mode') || '').toLowerCase();
    const source = (this.route.snapshot.queryParamMap.get('source') || '').toLowerCase();
    this.isEmergencyMode = mode === 'emergency';
    this.emergencySource = source;
  }

  submitPatientForm(): void {
    const idPersonnel = this.authService.getCurrentUser()?.id;
    if (!idPersonnel) {
      this.saveError = 'Utilisateur medical non identifie.';
      return;
    }

    const nom = this.patientForm.nom.trim();
    const prenom = this.patientForm.prenom.trim();
    const cin = this.patientForm.cin.trim();
    const telephone = this.patientForm.telephone.trim();
    const email = this.patientForm.email.trim();
    const agePatient = Number(this.patientForm.agePatient);

    if (!nom || !prenom || !cin) {
      this.saveError = 'Nom, prenom et CIN sont obligatoires.';
      return;
    }

    this.saving = true;
    this.saveError = '';
    this.saveMessage = '';

    this.rdvService.saveMedicalStaffPatient({
      idPersonnel,
      patient: {
        nom,
        prenom,
        cin,
        telephone: telephone || null,
        email: email || null
      }
    }).subscribe({
      next: (response) => {
        const savedPatientId = response.patient?.id;

        if (savedPatientId && this.patientForm.dateRDV) {
          // If RDV info is provided, create the RDV
          this.rdvService.addRdv({
            idPatient: savedPatientId,
            idPersonnel: idPersonnel,
            dateRDV: this.patientForm.dateRDV,
            heureDebut: this.patientForm.heureDebut,
            heureFin: this.patientForm.heureDebut, // Same as start if not provided
            motifConsultation: this.patientForm.motifConsultation,
            statut: this.patientForm.motifConsultation === 'urgence' ? 'Urgent' : 'Confirme',
            isUrgent: this.patientForm.motifConsultation === 'urgence',
            nom,
            prenom,
            telephone,
            email,
            agePatient
          }).subscribe({
            next: () => {
              this.saving = false;
              this.clearPatientForm();
              this.router.navigate([this.baseRoute, 'planning']);
            },
            error: (err) => {
              this.saving = false;
              this.saveError = err?.error?.error || 'Patient enregistré, mais échec lors de la création du RDV.';
            }
          });
        } else {
          this.saving = false;
          this.saveMessage = response.created
            ? 'Patient enregistré avec succès dans la base de données.'
            : 'Patient mis à jour avec succès dans la base de données.';
          this.clearPatientForm();
          if (savedPatientId) {
            this.router.navigate([this.baseRoute, 'patient-profile', savedPatientId]);
          }
        }
      },
      error: (error) => {
        this.saving = false;
        this.saveError = error?.error?.error || 'Impossible d\'enregistrer le patient.';
      }
    });
  }

  searchPatientByCin(): void {
    const cin = this.searchCin.trim();
    if (!cin) {
      this.searchMessage = 'Veuillez saisir un CIN.';
      return;
    }

    const idPersonnel = this.authService.getCurrentUser()?.id;
    if (!idPersonnel) {
      this.searchMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.searching = true;
    this.searchMessage = '';

    this.rdvService.findMedicalStaffPatientByCin(idPersonnel, cin).subscribe({
      next: (response) => {
        this.searching = false;
        if (response.found && response.patient?.id) {
          this.searchMessage = `Patient trouve: ${response.patient.prenom} ${response.patient.nom}. Ouverture du profil...`;
          this.router.navigate([this.baseRoute, 'patient-profile', response.patient.id]);
          return;
        }

        this.searchMessage = 'Aucun patient trouve avec ce CIN. Vous pouvez remplir le formulaire ci-dessous.';
        this.patientForm.cin = cin;
      },
      error: (error) => {
        this.searching = false;
        if (error?.status === 404) {
          this.searchMessage = 'Aucun patient trouve avec ce CIN. Vous pouvez remplir le formulaire ci-dessous.';
          this.patientForm.cin = cin;
          return;
        }

        this.searchMessage = error?.error?.error || 'Impossible de rechercher le patient par CIN.';
      }
    });
  }

  clearPatientForm(): void {
    this.patientForm = {
      nom: '',
      prenom: '',
      cin: '',
      telephone: '',
      email: '',
      agePatient: '',
      dateRDV: '',
      heureDebut: '',
      motifConsultation: 'consultation'
    };
    this.saveError = '';
    this.saveMessage = '';
  }
}

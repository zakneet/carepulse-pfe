import { Component, OnInit } from '@angular/core';
import { PatientDashboardMedicalRecord, RdvService } from '../services/rdv.service';

interface PatientProfile {
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
}

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profile: PatientProfile = {};
  dossierMedical: PatientDashboardMedicalRecord | null = null;
  loading = true;
  errorMessage = '';

  constructor(private readonly rdvService: RdvService) {}

  ngOnInit(): void {
    const stored = localStorage.getItem('patientProfile');
    if (stored) {
      try {
        this.profile = JSON.parse(stored) as PatientProfile;
      } catch {
        this.profile = {};
      }
    }

    this.rdvService.getPatientDashboard().subscribe({
      next: (response) => {
        this.profile = {
          nom: response.patient.nom,
          prenom: response.patient.prenom,
          email: response.patient.email || undefined,
          telephone: response.patient.telephone || undefined,
        };
        this.dossierMedical = response.dossierMedical;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger le dossier medical.';
      }
    });
  }
}

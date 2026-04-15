import { Component } from '@angular/core';
import { Router } from '@angular/router';
import {
  MedicalStaff,
  NewRdv,
  RdvService,
  SuggestedSlot
} from '../services/rdv.service';

@Component({
  selector: 'app-rdv-form',
  templateUrl: './rdv-form.component.html',
  styleUrls: ['./rdv-form.component.css']
})
export class RdvFormComponent {
  form: NewRdv = {
    idPatient: 0,
    idPersonnel: 0,
    dateRDV: '',
    heureDebut: '',
    heureFin: '',
    motifConsultation: 'consultation',
    agePatient: undefined
  };

  medicalStaff: MedicalStaff[] = [];
  availableSpecialites: string[] = [];
  filteredMedicalStaff: MedicalStaff[] = [];
  selectedSpecialite = '';
  suggestedSlots: SuggestedSlot[] = [];
  selectedSlot: SuggestedSlot | null = null;
  planningContext: { todayAppointments: number; weekAppointments: number } | null = null;
  isLoadingSlots = false;
  errorMessage = '';
  successMessage = '';
  isSubmitting = false;
  hasConflictError = false;

  constructor(private rdvService: RdvService, private router: Router) {
    const authUser = this.readStoredUser('authUser');
    const patientProfile = this.readStoredUser('patientProfile');
    this.form.idPatient = this.extractPatientId(authUser) || this.extractPatientId(patientProfile) || 0;

    this.loadMedicalStaff();
  }

  private loadMedicalStaff(): void {
    this.rdvService.getMedicalStaff().subscribe({
      next: (staff) => {
        this.medicalStaff = staff;
        this.availableSpecialites = this.extractSpecialites(staff);
        this.applySpecialiteFilter();
        if (staff.length === 0) {
          this.errorMessage = 'Aucun medecin disponible pour le moment.';
        } else {
          this.errorMessage = '';
        }
      },
      error: () => {
        this.errorMessage = 'Impossible de charger la liste des medecins.';
      }
    });
  }

  onSpecialiteChange(): void {
    this.form.idPersonnel = 0;
    this.suggestedSlots = [];
    this.selectedSlot = null;
    this.planningContext = null;
    this.applySpecialiteFilter();
  }

  private applySpecialiteFilter(): void {
    const specialite = (this.selectedSpecialite || '').trim().toLowerCase();

    this.filteredMedicalStaff = this.medicalStaff.filter((staff) => {
      if (!specialite) {
        return true;
      }
      return (staff.specialite || '').trim().toLowerCase() === specialite;
    });

    if (this.filteredMedicalStaff.length > 0) {
      const selectedStillExists = this.filteredMedicalStaff.some((staff) => staff.id === this.form.idPersonnel);
      if (!selectedStillExists) {
        this.form.idPersonnel = this.filteredMedicalStaff[0].id;
      }
      return;
    }

    this.form.idPersonnel = 0;
  }

  private extractSpecialites(staff: MedicalStaff[]): string[] {
    const set = new Set<string>();
    staff.forEach((person) => {
      const value = (person.specialite || '').trim();
      if (value) {
        set.add(value);
      }
    });
    return Array.from(set).sort((a, b) => a.localeCompare(b, 'fr'));
  }

  suggestSlots(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.suggestedSlots = [];
    this.selectedSlot = null;
    this.planningContext = null;

    if (!this.form.idPersonnel || !this.form.dateRDV) {
      this.errorMessage = 'Veuillez choisir un medecin et une date proposee.';
      return;
    }

    if (this.form.agePatient !== undefined && this.form.agePatient !== null) {
      if (this.form.agePatient <= 0 || this.form.agePatient > 130) {
        this.errorMessage = 'Age patient invalide.';
        return;
      }
    }

    this.isLoadingSlots = true;
    this.rdvService.suggestAvailableSlots({
      idPersonnel: this.form.idPersonnel,
      dateRDV: this.form.dateRDV,
      isUrgent: false,
      slotDuration: 30
    }).subscribe({
      next: (response) => {
        this.isLoadingSlots = false;
        this.suggestedSlots = response.suggestedSlots || [];
        this.planningContext = response.planningContext
          ? {
              todayAppointments: response.planningContext.todayAppointments,
              weekAppointments: response.planningContext.weekAppointments
            }
          : null;
        if (this.suggestedSlots.length === 0) {
          this.errorMessage = 'Aucun creneau disponible pour cette date. Essayez une autre date.';
        }
      },
      error: () => {
        this.isLoadingSlots = false;
        this.errorMessage = 'Impossible de proposer des creneaux pour ce medecin.';
      }
    });
  }

  chooseSlot(slot: SuggestedSlot): void {
    this.selectedSlot = slot;
    this.form.heureDebut = slot.heureDebut;
    this.form.heureFin = slot.heureFin;
  }

  retryAfterConflict(): void {
    this.hasConflictError = false;
    this.errorMessage = '';
    this.selectedSlot = null;
    this.form.heureDebut = '';
    this.form.heureFin = '';
    this.suggestSlots();
  }

  submit(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.form.idPersonnel || !this.form.dateRDV) {
      this.errorMessage = 'Veuillez completer medecin et date.';
      return;
    }

    if (!this.selectedSlot) {
      this.errorMessage = 'Veuillez choisir un creneau propose.';
      return;
    }

    this.isSubmitting = true;

    const payload: NewRdv = {
      ...this.form,
      nom: this.form.nom,
      prenom: this.form.prenom,
      idPatient: this.form.idPatient || 0,
      heureFin: this.form.heureFin || this.form.heureDebut,
      statut: this.form.motifConsultation
    };

    console.log('RDV Form - Submitting payload:', payload);

    this.rdvService.addRdv(payload).subscribe({
      next: (response: unknown) => {
        this.isSubmitting = false;
        
        console.log('RDV Form - Response received:', response);
        
        // If we got a response, the RDV was created successfully
        const data = (response || {}) as Record<string, unknown>;
        const rdv = (data['rdv'] || {}) as Record<string, unknown>;
        const createdId = Number(rdv['id'] || rdv['idRdv'] || rdv['idRDV']);
        
        console.log('RDV Form - Created ID:', createdId);
        
        if (createdId > 0) {
          // RDV was successfully created - always show success
          localStorage.setItem('planningRefreshSignal', `${payload.idPersonnel}:${payload.dateRDV}:${Date.now()}`);
          this.successMessage = 'Rendez-vous enregistre avec succes! Le medecin verra votre demande dans son planning.';
          this.errorMessage = '';
          console.log('RDV Form - Success message displayed');
          
          // Clear the form for a new booking
          setTimeout(() => {
            this.form.nom = '';
            this.form.prenom = '';
            this.form.agePatient = undefined;
            this.form.dateRDV = '';
            this.form.idPersonnel = 0;
            this.form.motifConsultation = 'consultation';
            this.selectedSlot = null;
            this.suggestedSlots = [];
            this.selectedSpecialite = '';
          }, 1000);
        } else {
          this.errorMessage = 'Reponse invalide du serveur. Verifiez votre connexion.';
          console.error('RDV Form - Invalid ID in response');
        }
      },
      error: (errorResponse) => {
        this.isSubmitting = false;
        
        // Handle conflict (409) errors specifically
        if (errorResponse?.status === 409) {
          this.hasConflictError = true;
          const conflictingApp = errorResponse?.error?.conflictingAppointment;
          if (conflictingApp) {
            const patientInfo = conflictingApp.patientPrenom 
              ? `${conflictingApp.patientPrenom} ${conflictingApp.patientNom}` 
              : conflictingApp.patientNom || 'Un patient';
            this.errorMessage = `Creneau indisponible: occupe par ${patientInfo} de ${conflictingApp.heureDebut} a ${conflictingApp.heureFin}. Veuillez choisir un autre creneau.`;
          } else {
            this.errorMessage = 'Le creneau demande est deja reserve. Veuillez choisir un autre creneau.';
          }
          return;
        }
        
        this.hasConflictError = false;
        this.errorMessage = errorResponse?.error?.error || "Impossible d'enregistrer le RDV. Verifiez le backend.";
      }
    });
  }

  private readStoredUser(key: string): Record<string, unknown> | null {
    const raw = localStorage.getItem(key);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as Record<string, unknown>;
    } catch {
      return null;
    }
  }

  private extractPatientId(user: Record<string, unknown> | null): number | null {
    if (!user) {
      return null;
    }
    const candidates = [user['id'], user['idPatient'], user['userId'], user['patientId']];
    for (const value of candidates) {
      const asNumber = Number(value);
      if (Number.isFinite(asNumber) && asNumber > 0) {
        return asNumber;
      }
    }
    return null;
  }

}

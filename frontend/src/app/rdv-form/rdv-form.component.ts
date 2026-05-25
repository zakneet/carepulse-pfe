import { Component } from '@angular/core';
import { forkJoin } from 'rxjs';
import { map } from 'rxjs/operators';
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
  private readonly draftStorageKey = 'rdvBookingDraft';

  form: NewRdv = {
    idPatient: 0,
    idPersonnel: 0,
    dateRDV: '',
    heureDebut: '',
    heureFin: '',
    motifConsultation: 'consultation',
    nom: '',
    prenom: '',
    telephone: ''
  };

  medicalStaff: MedicalStaff[] = [];
  availableSpecialites: string[] = [];
  availableRegions: string[] = [];
  filteredMedicalStaff: MedicalStaff[] = [];
  selectedRegion = '';
  step = 1; // 1 = choose spec/region/date, 2 = show doctors & schedules
  doctorsWithSlots: Array<{ staff: MedicalStaff; slots: SuggestedSlot[] }> = [];
  selectedSpecialite = '';
  suggestedSlots: SuggestedSlot[] = [];
  selectedSlot: SuggestedSlot | null = null;
  proposalIndex = 0;
  optionalDoctorId: number | null = null;
  planningContext: { todayAppointments: number; weekAppointments: number } | null = null;
  isLoadingSlots = false;
  errorMessage = '';
  successMessage = '';
  isSubmitting = false;
  hasConflictError = false;
  isOptimizingPlanning = false;
  optimizationMessage = '';

  constructor(
    private rdvService: RdvService,
    private router: Router
  ) {
    const authUser = this.readStoredUser('authUser');
    const patientProfile = this.readStoredUser('patientProfile');
    this.form.idPatient = this.extractPatientId(authUser) || this.extractPatientId(patientProfile) || 0;

    this.restoreDraft();

    this.loadMedicalStaff();
  }

  private loadMedicalStaff(): void {
    this.rdvService.getMedicalStaff().subscribe({
      next: (staff) => {
        this.medicalStaff = staff;
        this.availableSpecialites = this.extractSpecialites(staff);
        this.availableRegions = this.extractRegions(staff);
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

  private extractRegions(staff: MedicalStaff[]): string[] {
    // Try to build a region list from staff properties if present (flexible)
    const set = new Set<string>();
    staff.forEach((person) => {
      // prefer common keys if backend provides them
      const maybe = (person as any).region || (person as any).ville || (person as any).location || (person as any).city || '';
      const value = String(maybe || '').trim();
      if (value) set.add(value);
    });
    if (set.size === 0) {
      // fallback: generic list
      return ['Toutes'];
    }
    return ['Toutes', ...Array.from(set).sort((a, b) => a.localeCompare(b, 'fr'))];
  }

  onSpecialiteChange(): void {
    this.form.idPersonnel = 0;
    this.suggestedSlots = [];
    this.selectedSlot = null;
    this.proposalIndex = 0;
    this.planningContext = null;
    this.applySpecialiteFilter();
  }

  onRegionChange(): void {
    // Re-apply filter if region influences list
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

    // apply region filter if available and not 'Toutes'
    const region = (this.selectedRegion || '').trim();
    if (region && region !== 'Toutes') {
      this.filteredMedicalStaff = this.filteredMedicalStaff.filter((s) => {
        const maybe = (s as any).region || (s as any).ville || (s as any).location || (s as any).city || '';
        return String(maybe || '').trim() === region;
      });
    }

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

    this.isLoadingSlots = true;
    const requestPayload = {
      idPersonnel: this.form.idPersonnel,
      dateRDV: this.form.dateRDV,
      isUrgent: false,
      slotDuration: 30,
      proposalIndex: this.proposalIndex
    };

    this.rdvService.suggestAvailableSlots(requestPayload as any).subscribe({
      next: (response) => {
        this.isLoadingSlots = false;
        this.suggestedSlots = (response.optimizedSuggestedSlots && response.optimizedSuggestedSlots.length > 0)
          ? response.optimizedSuggestedSlots
          : (response.suggestedSlots || []);
        this.planningContext = response.planningContext
          ? {
              todayAppointments: response.planningContext.todayAppointments,
              weekAppointments: response.planningContext.weekAppointments
            }
          : null;
        if (this.suggestedSlots.length > 0) {
          this.chooseSlot(this.suggestedSlots[0]);
          return;
        }

        this.selectedSlot = null;
        this.form.heureDebut = '';
        this.form.heureFin = '';

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

  refreshSuggestedSlot(): void {
    this.proposalIndex += 1;
    this.suggestSlots();
  }

  // New: validate specialty/region/date and load doctors' available slots
  searchDoctorsAndSlots(): void {
    this.errorMessage = '';
    this.successMessage = '';
    if (!this.selectedSpecialite) {
      this.errorMessage = 'Veuillez choisir une spécialité.';
      return;
    }
    if (!this.form.dateRDV) {
      this.errorMessage = 'Veuillez choisir une date pour consulter les disponibilités.';
      return;
    }

    // Filter staff and for each fetch suggested slots for the selected date
    this.applySpecialiteFilter();
    let doctors = this.filteredMedicalStaff.slice();
    this.proposalIndex = 0;

    // if user selected an optional specific doctor, narrow to that doctor
    if (this.optionalDoctorId && Number.isFinite(this.optionalDoctorId)) {
      doctors = doctors.filter((d) => d.id === this.optionalDoctorId);
      // ensure form.idPersonnel reflects the optional doctor for later submission
      if (doctors.length > 0) {
        this.form.idPersonnel = doctors[0].id;
      }
    }
    if (doctors.length === 0) {
      this.errorMessage = 'Aucun medecin correspondant a ces criteres.';
      return;
    }

    this.doctorsWithSlots = [];
    this.isLoadingSlots = true;

    // For each doctor, call suggestAvailableSlots and collect results
    const observables = doctors.map((d) =>
      this.rdvService.suggestAvailableSlots({ idPersonnel: d.id, dateRDV: this.form.dateRDV, isUrgent: false, slotDuration: 30 }).pipe(
        // map response to object
        map((res) => ({
          staff: d,
          slots: (res.optimizedSuggestedSlots && res.optimizedSuggestedSlots.length > 0)
            ? res.optimizedSuggestedSlots
            : (res.suggestedSlots || [])
        }))
      )
    );

    forkJoin(observables).subscribe({
      next: (results: any[]) => {
        this.isLoadingSlots = false;
        // Order doctors by available slots count desc (proxy for rate)
        this.doctorsWithSlots = results
          .map((r) => ({ staff: r.staff as MedicalStaff, slots: r.slots as SuggestedSlot[] }))
          .sort((a, b) => (b.slots.length - a.slots.length));

        this.step = 2;
      },
      error: () => {
        this.isLoadingSlots = false;
        this.errorMessage = 'Impossible de charger les disponibilites des medecins.';
      }
    });
  }

  optimizeAndPersistPlanning(): void {
    this.errorMessage = '';
    this.optimizationMessage = '';

    if (!this.form.idPersonnel || !this.form.dateRDV) {
      this.errorMessage = 'Veuillez choisir un medecin et une date avant d’optimiser le planning.';
      return;
    }

    this.isOptimizingPlanning = true;
    this.rdvService.optimizeAndPersistDoctorPlanning(this.form.idPersonnel, this.form.dateRDV).subscribe({
      next: (response) => {
        this.isOptimizingPlanning = false;
        const updatedCount = response.updatedRows?.length || 0;
        this.optimizationMessage = updatedCount > 0
          ? `Planning optimise et enregistre: ${updatedCount} rendez-vous ajustes.`
          : 'Planning optimise et enregistre.';

        // Refresh available slots after persistence so the UI reflects the new planning.
        this.searchDoctorsAndSlots();
      },
      error: () => {
        this.isOptimizingPlanning = false;
        this.errorMessage = 'Impossible d’optimiser et d’enregistrer le planning pour ce medecin.';
      }
    });
  }

  // Choose a slot coming from a doctor's card
  chooseDoctorSlot(staffId: number, slot: SuggestedSlot): void {
    this.form.idPersonnel = staffId;
    this.form.dateRDV = this.form.dateRDV;
    this.chooseSlot(slot);
    // keep the UI at step 2 so user can submit
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

    if (!this.form.nom?.trim() || !this.form.prenom?.trim()) {
      this.errorMessage = 'Veuillez renseigner le nom et le prenom du patient.';
      return;
    }

    this.hasConflictError = false;
    this.isSubmitting = true;

    if (this.selectedSlot) {
      this.createRdv();
      return;
    }

    this.rdvService.suggestAvailableSlots({
      idPersonnel: this.form.idPersonnel,
      dateRDV: this.form.dateRDV,
      isUrgent: false,
      slotDuration: 30
    }).subscribe({
      next: (response) => {
        this.suggestedSlots = response.suggestedSlots || [];
        this.planningContext = response.planningContext
          ? {
              todayAppointments: response.planningContext.todayAppointments,
              weekAppointments: response.planningContext.weekAppointments
            }
          : null;

        if (this.suggestedSlots.length === 0) {
          this.isSubmitting = false;
          this.errorMessage = 'Aucun creneau disponible pour cette date. Essayez une autre date.';
          return;
        }

        this.isSubmitting = false;
        this.errorMessage = 'Veuillez choisir un creneau propose par OR-Tools avant de valider.';
      },
      error: () => {
        this.isSubmitting = false;
        this.errorMessage = 'Impossible de proposer des creneaux pour ce medecin.';
      }
    });
  }

  private createRdv(): void {
    if (!this.selectedSlot) {
      this.isSubmitting = false;
      this.errorMessage = 'Veuillez choisir un creneau propose.';
      return;
    }

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
          this.clearDraft();
          console.log('RDV Form - Success message displayed');
          
          // Clear the form for a new booking
          setTimeout(() => {
            this.form.nom = '';
            this.form.prenom = '';
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

  private persistDraft(): void {
    const draft = {
      form: this.form,
      selectedSpecialite: this.selectedSpecialite,
      selectedSlot: this.selectedSlot,
      suggestedSlots: this.suggestedSlots,
      planningContext: this.planningContext,
      optionalDoctorId: this.optionalDoctorId,
    };
    sessionStorage.setItem(this.draftStorageKey, JSON.stringify(draft));
  }

  private restoreDraft(): void {
    const raw = sessionStorage.getItem(this.draftStorageKey);
    if (!raw) {
      return;
    }

    try {
      const draft = JSON.parse(raw) as {
        form?: Partial<NewRdv>;
        selectedSpecialite?: string;
        selectedSlot?: SuggestedSlot | null;
        suggestedSlots?: SuggestedSlot[];
        planningContext?: { todayAppointments: number; weekAppointments: number } | null;
        optionalDoctorId?: number | null;
      };

      this.form = {
        ...this.form,
        ...(draft.form || {}),
      };
      this.selectedSpecialite = draft.selectedSpecialite || '';
      this.selectedSlot = draft.selectedSlot || null;
      this.suggestedSlots = Array.isArray(draft.suggestedSlots) ? draft.suggestedSlots : [];
      this.planningContext = draft.planningContext || null;
      this.optionalDoctorId = typeof draft.optionalDoctorId === 'number' ? draft.optionalDoctorId : null;

      if (this.form.idPersonnel) {
        this.applySpecialiteFilter();
      }
    } catch {
      this.clearDraft();
    }
  }

  private clearDraft(): void {
    sessionStorage.removeItem(this.draftStorageKey);
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

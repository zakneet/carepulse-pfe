import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';

interface BookingFormData {
  firstName: string;
  lastName: string;
  email: string;
  age: string;
  phone: string;
  specialite: string;
  date: string;
  timePreference: 'matin' | 'apres-midi' | 'peu-importe';
}

@Component({
  selector: 'app-booking',
  templateUrl: './booking.component.html',
  styleUrls: ['./booking.component.css']
})
export class BookingComponent implements OnInit {
  doctorId: string | null = null;
  doctorDetails: any = null;
  doctors: any[] = [];

  formData: BookingFormData = {
    firstName: '',
    lastName: '',
    email: '',
    age: '',
    phone: '',
    specialite: '',
    date: '',
    timePreference: 'peu-importe'
  };

  step: 'form' | 'loading' | 'result' = 'form';
  optimizationResult: any = null;
  errorMessage = '';
  successMessage = '';
  isConfirming = false;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.doctorId = params.get('id');
      this.loadDoctors();
    });

    this.route.queryParams.subscribe(q => {
      if (q['doctorId']) {
        this.doctorId = String(q['doctorId']);
      }
      if (q['specialite']) {
        this.formData.specialite = q['specialite'];
        this.loadDoctors(q['specialite']);
      } else if (this.doctorId) {
        this.loadDoctors();
      }
    });
  }

  loadDoctors(specialite?: string): void {
    const query = specialite ? `?specialite=${encodeURIComponent(specialite)}` : '';
    this.http.get<any[]>(`http://localhost:5000/medical-staff${query}`).subscribe({
      next: (res) => {
        this.doctors = Array.isArray(res) ? res : [];
        this.syncSelectedDoctor();

        if (!this.doctorId && this.doctors.length === 1) {
          this.doctorId = String(this.doctors[0].id ?? this.doctors[0].id_personnel ?? '');
          this.syncSelectedDoctor();
        }
      },
      error: (err) => console.error(err)
    });
  }

  onDoctorChange(): void {
    this.syncSelectedDoctor();
  }

  private syncSelectedDoctor(): void {
    if (!this.doctorId) {
      this.doctorDetails = null;
      return;
    }

    const selectedDoctor = this.doctors.find((doc) => String(doc.id ?? doc.id_personnel) === String(this.doctorId));
    this.doctorDetails = selectedDoctor || null;
    if (this.doctorDetails) {
      this.formData.specialite = this.doctorDetails.specialite || this.formData.specialite;
    }
  }

  /** Build patient identity from form — supports full name in lastName field. */
  private resolvePatientIdentity(): { firstName: string; lastName: string } | null {
    let firstName = this.formData.firstName.trim();
    let lastName = this.formData.lastName.trim();

    if (!firstName && lastName.includes(' ')) {
      const parts = lastName.split(/\s+/).filter(Boolean);
      firstName = parts.shift() || '';
      lastName = parts.join(' ');
    }

    if (!firstName || !lastName) {
      return null;
    }

    return { firstName, lastName };
  }

  private buildBookingPayload(extra: Record<string, unknown> = {}): Record<string, unknown> | null {
    const identity = this.resolvePatientIdentity();
    if (!identity) {
      return null;
    }

    return {
      firstName: identity.firstName,
      lastName: identity.lastName,
      prenom: identity.firstName,
      nom: identity.lastName,
      phone: this.formData.phone.trim(),
      telephone: this.formData.phone.trim(),
      email: this.formData.email.trim(),
      age: Number(this.formData.age),
      specialite: this.formData.specialite,
      date: this.formData.date,
      idPersonnel: this.doctorId,
      timePreference: this.formData.timePreference,
      fromPublicBooking: true,
      ...extra
    };
  }

  submitSmartBooking(): void {
    const identity = this.resolvePatientIdentity();
    if (!identity || !this.formData.age || !this.formData.phone || !this.formData.date) {
      this.errorMessage = 'Veuillez remplir tous les champs obligatoires (prénom, nom, téléphone, âge, date).';
      return;
    }

    if (!this.doctorId && !this.formData.specialite) {
      this.errorMessage = 'Veuillez spécifier une spécialité souhaitée.';
      return;
    }

    const payload = this.buildBookingPayload({ rejectedSlots: [] });
    if (!payload) {
      this.errorMessage = 'Veuillez saisir le prénom et le nom du patient.';
      return;
    }

    this.errorMessage = '';
    this.step = 'loading';

    this.http.post<any>('http://localhost:5000/appointments/smart-booking', payload).subscribe({
      next: (res: any) => {
        setTimeout(() => {
          this.optimizationResult = res;
          this.step = 'result';
        }, 1500);
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Erreur lors de l\'optimisation du planning.';
        this.step = 'form';
      }
    });
  }

  requestAlternativeSlot(): void {
    this.step = 'loading';
    const payload = this.buildBookingPayload({
      rejectedSlots: [this.optimizationResult.slot]
    });

    if (!payload) {
      this.errorMessage = 'Informations patient invalides.';
      this.step = 'result';
      return;
    }

    this.http.post<any>('http://localhost:5000/appointments/alternative-slot', payload).subscribe({
      next: (res) => {
        setTimeout(() => {
          this.optimizationResult = res;
          this.step = 'result';
        }, 1000);
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Aucune alternative trouvée.';
        this.step = 'result';
      }
    });
  }

  confirmAppointment(): void {
    const selectedDoctorId = Number(
      this.doctorId
      || this.optimizationResult?.doctor?.id
      || this.optimizationResult?.doctor?.id_personnel
      || 0
    );

    if (!this.optimizationResult?.slot || !selectedDoctorId) {
      this.errorMessage = 'Aucun rendez-vous à confirmer.';
      return;
    }

    const identity = this.resolvePatientIdentity();
    if (!identity) {
      this.errorMessage = 'Veuillez saisir le prénom et le nom du patient.';
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';
    this.isConfirming = true;

    const slotStart = this.formatTime(this.optimizationResult.slot.start);
    const slotEnd = this.formatTime(this.optimizationResult.slot.end);
    const slotDuration = (this.optimizationResult.slot.end - this.optimizationResult.slot.start) || 30;

    const payload = {
      firstName: identity.firstName,
      lastName: identity.lastName,
      prenom: identity.firstName,
      nom: identity.lastName,
      phone: this.formData.phone.trim(),
      telephone: this.formData.phone.trim(),
      email: this.formData.email.trim(),
      agePatient: Number(this.formData.age),
      idPersonnel: selectedDoctorId,
      dateRDV: this.formData.date,
      heureDebut: slotStart,
      heureFin: slotEnd,
      slotDuration,
      motifConsultation: 'consultation',
      statut: 'consultation',
      fromSmartBooking: true,
      fromPublicBooking: true
    };

    console.log('[Booking] confirmAppointment — patient:', `${identity.firstName} ${identity.lastName}`);

    this.http.post<any>('http://localhost:5000/add_rdv', payload).subscribe({
      next: () => {
        this.isConfirming = false;
        this.successMessage = `✓ Demande enregistrée — en attente de confirmation par le médecin.`;
        setTimeout(() => this.router.navigate(['/home']), 1500);
      },
      error: (err) => {
        this.isConfirming = false;
        const backendMsg = err.error?.error || err.error?.message || null;
        this.errorMessage = backendMsg
          ? `Impossible de confirmer le rendez-vous : ${backendMsg}`
          : 'Erreur lors de la confirmation. Veuillez réessayer.';
        console.error('[Booking] /add_rdv error:', err.status, err.error);
      }
    });
  }

  formatTime(minutes: number): string {
    const h = Math.floor(minutes / 60);
    const m = Math.floor(minutes % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
  }
}

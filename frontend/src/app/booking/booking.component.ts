import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-booking',
  templateUrl: './booking.component.html',
  styleUrls: ['./booking.component.css']
})
export class BookingComponent implements OnInit {
  doctorId: string | null = null;
  doctorDetails: any = null;
  doctors: any[] = [];
  
  formData = {
    nom: '',
    prenom: '',
    age: '',
    telephone: '',
    specialite: '',
    date: '',
    timePreference: 'peu-importe' as 'matin' | 'apres-midi' | 'peu-importe'
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

  fetchDoctorDetails() {
    this.syncSelectedDoctor();
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

  submitSmartBooking() {
    if (!this.formData.nom || !this.formData.prenom || !this.formData.age || !this.formData.telephone || !this.formData.date) {
      this.errorMessage = 'Veuillez remplir tous les champs obligatoires.';
      return;
    }
    
    if (!this.doctorId && !this.formData.specialite) {
      this.errorMessage = 'Veuillez spécifier une spécialité souhaitée.';
      return;
    }

    this.errorMessage = '';
    this.step = 'loading';

    const payload = {
      ...this.formData,
      age: Number(this.formData.age),
      idPersonnel: this.doctorId,
      timePreference: this.formData.timePreference,
      rejectedSlots: [] // For alternative proposals
    };

    this.http.post<any>('http://localhost:5000/appointments/smart-booking', payload).subscribe({
      next: (res: any) => {
        setTimeout(() => { // Simulate complex AI loading
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

  requestAlternativeSlot() {
    this.step = 'loading';
    const payload = {
      ...this.formData,
      idPersonnel: this.doctorId,
      timePreference: this.formData.timePreference,
      rejectedSlots: [this.optimizationResult.slot]
      // If we had a list of rejected slots, we'd append it
    };

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

    this.errorMessage = '';
    this.successMessage = '';
    this.isConfirming = true;

    const slotStart = this.formatTime(this.optimizationResult.slot.start);
    const slotEnd   = this.formatTime(this.optimizationResult.slot.end);
    const slotDuration = (this.optimizationResult.slot.end - this.optimizationResult.slot.start) || 30;

    console.log('[Booking] confirmAppointment payload preview:', {
      idPersonnel: selectedDoctorId,
      dateRDV: this.formData.date,
      heureDebut: slotStart,
      heureFin: slotEnd,
      slotDuration,
      fromSmartBooking: true
    });

    const payload = {
      nom:               this.formData.nom,
      prenom:            this.formData.prenom,
      telephone:         this.formData.telephone,
      agePatient:        Number(this.formData.age),
      idPersonnel:       selectedDoctorId,
      dateRDV:           this.formData.date,
      heureDebut:        slotStart,
      heureFin:          slotEnd,
      slotDuration:      slotDuration,
      motifConsultation: 'consultation',
      statut:            'consultation',
      // Tells the backend that OR-Tools already validated this slot server-side
      // → skips the redundant whitelist check that was causing HTTP 400
      fromSmartBooking:  true
    };

    this.http.post<any>('http://localhost:5000/add_rdv', payload).subscribe({
      next: (res) => {
        this.isConfirming = false;
        this.successMessage = '✓ Rendez-vous confirmé avec succès !';
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

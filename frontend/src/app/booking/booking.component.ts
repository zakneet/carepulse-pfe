import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-booking',
  templateUrl: './booking.component.html',
  styleUrls: ['./booking.component.css']
})
export class BookingComponent implements OnInit {
  doctorId: string | null = null;
  doctorDetails: any = null;
  
  formData = {
    nom: '',
    prenom: '',
    telephone: '',
    specialite: '',
    date: ''
  };

  step: 'form' | 'loading' | 'result' = 'form';
  optimizationResult: any = null;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.doctorId = params.get('id');
      if (this.doctorId) {
        this.fetchDoctorDetails();
      }
    });

    this.route.queryParams.subscribe(q => {
      if (q['specialite']) this.formData.specialite = q['specialite'];
    });
  }

  fetchDoctorDetails() {
    this.http.get<any>(`http://localhost:5000/medical-staff?id=${this.doctorId}`).subscribe({
      next: (res) => {
        const dataArray = Array.isArray(res) ? res : (res.data || []);
        if (dataArray.length > 0) {
          this.doctorDetails = dataArray[0];
          this.formData.specialite = this.doctorDetails.specialite || this.formData.specialite;
        }
      },
      error: (err) => console.error(err)
    });
  }

  submitSmartBooking() {
    if (!this.formData.nom || !this.formData.prenom || !this.formData.telephone || !this.formData.date) {
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
      idPersonnel: this.doctorId,
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

  formatTime(minutes: number): string {
    const h = Math.floor(minutes / 60);
    const m = Math.floor(minutes % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
  }
}

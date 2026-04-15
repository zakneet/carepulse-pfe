import { Component } from '@angular/core';
import { Rdv, RdvService } from 'src/app/services/rdv.service';

@Component({
  selector: 'app-medical-staff-appointments',
  templateUrl: './medical-staff-appointments.component.html',
  styleUrls: ['./medical-staff-appointments.component.css']
})
export class MedicalStaffAppointmentsComponent {
  loading = false;
  errorMessage = '';
  appointments: Rdv[] = [];

  constructor(private rdvService: RdvService) {
    this.loadAppointments();
  }

  private loadAppointments(): void {
    this.loading = true;
    this.errorMessage = '';

    this.rdvService.getRdvs().subscribe({
      next: (rdvs) => {
        this.loading = false;
        this.appointments = rdvs || [];
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger les rendez-vous.';
      }
    });
  }
}

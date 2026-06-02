import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { MedicalStaffApiService } from '../../services/medical-staff-api.service';
import { MedicalStaffDashboardResponse } from '../../services/medical-staff-dashboard.service';

@Component({
  selector: 'app-medical-staff-appointments',
  templateUrl: './medical-staff-appointments.component.html',
  styleUrls: ['./medical-staff-appointments.component.css']
})
export class MedicalStaffAppointmentsComponent implements OnInit {
  loading = false;
  errorMessage = '';
  dashboard: MedicalStaffDashboardResponse | null = null;
  showEmergencyModal = false;

  constructor(private authService: AuthService, private api: MedicalStaffApiService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    const id = this.getPersonnelId();
    if (!id) {
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.api.getDashboard(id).subscribe({
      next: (data) => {
        this.dashboard = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger les urgences.';
      }
    });
  }

  get emergencyAppointments() {
    return (this.dashboard?.todayAppointments || []).filter((a) => a.isEmergency);
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; id_personnel?: number } | null;
    return user?.id ?? user?.id_personnel;
  }
}

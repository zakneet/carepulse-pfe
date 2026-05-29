import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { AuthUser } from 'src/app/models/auth.model';

@Component({
  selector: 'app-medical-staff-dashboard',
  templateUrl: './medical-staff-dashboard.component.html',
  styleUrls: ['./medical-staff-dashboard.component.css']
})
export class MedicalStaffDashboardComponent implements OnInit {

  currentUser: AuthUser | null = null;
  staffView: 'doctor' | 'nurse' = 'doctor';

  stats = {
    appointments: 14,
    urgencies: 2,
    optimizationRate: 86,
    optimizationDelta: 8,
    timeSaved: '6.4h'
  };

  nextAppointments = [
    {
      time: '09:00',
      patient: 'Sophie Laurent',
      motif: 'Cardiology follow-up',
      status: 'Optimized',
      statusColor: 'blue'
    },
    {
      time: '09:45',
      patient: 'Marc Dubois',
      motif: 'Acute chest pain',
      status: 'Emergency',
      statusColor: 'red'
    },
    {
      time: '10:30',
      patient: 'Anna Petit',
      motif: 'Annual check-up',
      status: 'Optimized',
      statusColor: 'blue'
    },
    {
      time: '11:15',
      patient: 'Alice Martin',
      motif: 'Consultation Générale',
      status: 'En salle d\'attente',
      statusColor: 'emerald'
    },
    {
      time: '12:00',
      patient: 'Pierre Vidal',
      motif: 'Suivi de traitement',
      status: 'Confirmé',
      statusColor: 'amber'
    }
  ];

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.staffView = this.authService.isNurse() ? 'nurse' : 'doctor';
  }

  openPlanning(): void {
    const base = this.authService.getMedicalStaffBaseRoute();
    this.router.navigate([base + '/planning-full']);
  }

  openEmergency(): void {
    // Navigate to emergencies or open form — for now scroll to planning
    const base = this.authService.getMedicalStaffBaseRoute();
    this.router.navigate([base + '/planning-full']);
  }

  getAvatarGradient(color: string): string {
    const map: Record<string, string> = {
      blue: 'linear-gradient(135deg, #0284c7, #38bdf8)',
      emerald: 'linear-gradient(135deg, #059669, #34d399)',
      red: 'linear-gradient(135deg, #dc2626, #f87171)',
      amber: 'linear-gradient(135deg, #d97706, #fbbf24)'
    };
    return map[color] || map['blue'];
  }
}

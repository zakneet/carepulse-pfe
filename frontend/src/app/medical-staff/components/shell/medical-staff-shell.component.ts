import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from 'src/app/services/auth.service';
import { SocketService } from 'src/app/services/socket.service';
import { MedicalStaffDashboardService } from '../../services/medical-staff-dashboard.service';

@Component({
  selector: 'app-medical-staff-shell',
  templateUrl: './medical-staff-shell.component.html',
  styleUrls: ['./medical-staff-shell.component.css']
})
export class MedicalStaffShellComponent implements OnInit, OnDestroy {
  currentDoctor = 'Médecin';
  currentSpecialty = 'Médecine générale';
  baseRoute = '/medical-staff/doctor';

  emergencyBadge = 0;
  waitingBadge = 0;
  optimizationScore = 0;

  private dashboardSub?: Subscription;
  private socketSubs: Subscription[] = [];

  constructor(
    private authService: AuthService,
    private router: Router,
    private dashboardService: MedicalStaffDashboardService,
    private socketService: SocketService
  ) {}

  ngOnInit(): void {
    const user = this.authService.getCurrentUser();
    if (user) {
      this.currentDoctor = `${user.prenom || ''} ${user.nom || ''}`.trim() || 'Médecin';
      this.currentSpecialty = user.specialite || 'Médecine générale';
    }

    this.baseRoute = this.authService.getMedicalStaffBaseRoute();
    this.loadNavBadges();
    this.setupLiveBadges();
  }

  ngOnDestroy(): void {
    this.dashboardSub?.unsubscribe();
    this.socketSubs.forEach((sub) => sub.unsubscribe());
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/medical-staff/authenticate']);
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as {
      id?: number;
      idPersonnel?: number;
      id_personnel?: number;
    } | null;
    return user?.id ?? user?.idPersonnel ?? user?.id_personnel;
  }

  private loadNavBadges(): void {
    const idPersonnel = this.getPersonnelId();
    if (!idPersonnel) {
      return;
    }

    this.dashboardSub?.unsubscribe();
    this.dashboardSub = this.dashboardService.getDashboard(idPersonnel).subscribe({
      next: (data) => {
        this.emergencyBadge = data.emergencies;
        this.waitingBadge = data.waitingList;
        this.optimizationScore = data.optimizationScore;
      },
      error: () => {
        this.emergencyBadge = 0;
        this.waitingBadge = 0;
        this.optimizationScore = 0;
      }
    });
  }

  private setupLiveBadges(): void {
    this.socketService.connect();
    this.socketSubs.push(
      this.socketService.onEvent('doctor_planning_rearranged').subscribe((data) => {
        if (data?.idPersonnel === this.getPersonnelId()) {
          this.loadNavBadges();
        }
      }),
      this.socketService.onEvent('doctor_planning_cancelled').subscribe((data) => {
        if (data?.idPersonnel === this.getPersonnelId()) {
          this.loadNavBadges();
        }
      })
    );
  }
}

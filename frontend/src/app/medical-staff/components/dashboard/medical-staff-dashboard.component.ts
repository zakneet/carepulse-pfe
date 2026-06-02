import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription, interval } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { AuthService } from 'src/app/services/auth.service';
import { AuthUser } from 'src/app/models/auth.model';
import { SocketService } from 'src/app/services/socket.service';
import {
  DashboardAppointment,
  DashboardEmergencyAlert,
  MedicalStaffDashboardResponse,
  MedicalStaffDashboardService
} from '../../services/medical-staff-dashboard.service';

@Component({
  selector: 'app-medical-staff-dashboard',
  templateUrl: './medical-staff-dashboard.component.html',
  styleUrls: ['./medical-staff-dashboard.component.css']
})
export class MedicalStaffDashboardComponent implements OnInit, OnDestroy {

  currentUser: AuthUser | null = null;
  staffView: 'doctor' | 'nurse' = 'doctor';
  loading = true;
  errorMessage = '';

  stats = {
    appointments: 0,
    urgencies: 0,
    waitingList: 0,
    optimizationRate: 0,
    optimizationDelta: 0,
    appointmentsNextHour: 0,
    criticalEmergencies: 0,
    highPriorityWaiting: 0
  };

  optimizationMetrics = {
    schedulingEfficiency: 0,
    slotUtilization: 0,
    autoReplacements: 0
  };

  nextAppointments: DashboardAppointment[] = [];
  emergencyAlerts: DashboardEmergencyAlert[] = [];
  nextAppointment: DashboardAppointment | null = null;
  doctorAvailable = true;
  occupancyPercent = 0;
  animatedOptimizationScore = 0;

  private refreshSub?: Subscription;
  private socketSubs: Subscription[] = [];
  private pollSub?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router,
    private dashboardService: MedicalStaffDashboardService,
    private socketService: SocketService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.staffView = this.authService.isNurse() ? 'nurse' : 'doctor';
    this.loadDashboard();
    this.setupLiveRefresh();
  }

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
    this.pollSub?.unsubscribe();
    this.socketSubs.forEach((sub) => sub.unsubscribe());
  }

  openPlanning(): void {
    const base = this.authService.getMedicalStaffBaseRoute();
    this.router.navigate([base + '/planning']);
  }

  openEmergency(): void {
    const base = this.authService.getMedicalStaffBaseRoute();
    this.router.navigate([base + '/appointments']);
  }

  openWaitingList(): void {
    const base = this.authService.getMedicalStaffBaseRoute();
    this.router.navigate([base + '/waiting-list']);
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

  getAlertClass(severity: string): string {
    switch (severity) {
      case 'critical':
        return 'dash-alert--red';
      case 'high':
        return 'dash-alert--orange';
      default:
        return 'dash-alert--blue';
    }
  }

  getAlertIconClass(severity: string): string {
    switch (severity) {
      case 'critical':
        return 'dash-alert-icon--red';
      case 'high':
        return 'dash-alert-icon--orange';
      default:
        return 'dash-alert-icon--blue';
    }
  }

  loadDashboard(): void {
    const idPersonnel = this.getPersonnelId();
    if (!idPersonnel) {
      this.loading = false;
      this.errorMessage = 'Utilisateur médical non identifié.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.refreshSub?.unsubscribe();
    this.refreshSub = this.dashboardService
      .getDashboard(idPersonnel)
      .pipe(finalize(() => {
        this.loading = false;
      }))
      .subscribe({
        next: (data) => this.applyDashboard(data),
        error: () => {
          this.errorMessage = 'Impossible de charger le tableau de bord.';
        }
      });
  }

  private getPersonnelId(): number | undefined {
    const user = this.currentUser as AuthUser & { idPersonnel?: number; id_personnel?: number };
    return user?.id ?? user?.idPersonnel ?? user?.id_personnel;
  }

  private applyDashboard(data: MedicalStaffDashboardResponse): void {
    this.stats = {
      appointments: data.appointmentsToday,
      urgencies: data.emergencies,
      waitingList: data.waitingList,
      optimizationRate: data.optimizationScore,
      optimizationDelta: Math.max(0, data.optimizationScore - Math.max(0, data.optimizationScore - 8)),
      appointmentsNextHour: data.appointmentsNextHour,
      criticalEmergencies: data.criticalEmergencies,
      highPriorityWaiting: data.highPriorityWaiting
    };

    this.optimizationMetrics = {
      schedulingEfficiency: data.schedulingEfficiency,
      slotUtilization: data.slotUtilization,
      autoReplacements: data.autoReplacements
    };

    this.nextAppointments = data.todayAppointments || [];
    this.emergencyAlerts = data.emergencyAlerts || [];
    this.nextAppointment = data.nextAppointment || (data.todayAppointments?.[0] ?? null);
    this.doctorAvailable = data.doctorAvailable !== false;
    this.occupancyPercent = data.occupancyPercent ?? data.optimizationScore;
    this.animateOptimizationScore(data.optimizationScore);
  }

  private animateOptimizationScore(target: number): void {
    const duration = 800;
    const start = this.animatedOptimizationScore;
    const startTime = performance.now();

    const step = (now: number) => {
      const progress = Math.min(1, (now - startTime) / duration);
      this.animatedOptimizationScore = Math.round(start + (target - start) * progress);
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    requestAnimationFrame(step);
  }

  private setupLiveRefresh(): void {
    this.socketService.connect();
    this.socketSubs.push(
      this.socketService.onEvent('doctor_planning_rearranged').subscribe((data) => {
        if (data?.idPersonnel === this.getPersonnelId()) {
          this.loadDashboard();
        }
      }),
      this.socketService.onEvent('doctor_planning_cancelled').subscribe((data) => {
        if (data?.idPersonnel === this.getPersonnelId()) {
          this.loadDashboard();
        }
      })
    );

    this.pollSub = interval(60000).subscribe(() => this.loadDashboard());
  }
}

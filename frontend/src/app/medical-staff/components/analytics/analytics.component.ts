import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { MedicalStaffApiService } from '../../services/medical-staff-api.service';

@Component({
  selector: 'app-analytics',
  templateUrl: './analytics.component.html',
  styleUrls: ['./analytics.component.css']
})
export class AnalyticsComponent implements OnInit {
  loading = true;
  errorMessage = '';
  period: 'week' | 'month' | 'quarter' = 'week';
  kpis: Array<{ label: string; value: string; trend: string; color: string }> = [];
  trend: Array<{ date: string; count: number }> = [];
  maxBar = 1;

  constructor(private authService: AuthService, private api: MedicalStaffApiService) {}

  ngOnInit(): void {
    this.load();
  }

  setPeriod(period: 'week' | 'month' | 'quarter'): void {
    this.period = period;
    this.load();
  }

  load(): void {
    const id = this.getPersonnelId();
    if (!id) {
      this.loading = false;
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.api.getAnalytics(id, this.period).subscribe({
      next: (res) => {
        this.kpis = res.kpis || [];
        this.trend = res.trend || [];
        this.maxBar = Math.max(1, ...this.trend.map((t) => t.count));
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger les analyses.';
      }
    });
  }

  barHeight(count: number): number {
    return Math.round((count / this.maxBar) * 100);
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; id_personnel?: number } | null;
    return user?.id ?? user?.id_personnel;
  }
}

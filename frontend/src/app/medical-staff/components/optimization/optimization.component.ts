import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { MedicalStaffApiService, OptimizationMetric, OptimizationRecommendation } from '../../services/medical-staff-api.service';

@Component({
  selector: 'app-optimization',
  templateUrl: './optimization.component.html',
  styleUrls: ['./optimization.component.css']
})
export class OptimizationComponent implements OnInit {
  loading = true;
  errorMessage = '';
  score = 0;
  metrics: OptimizationMetric[] = [];
  recommendations: OptimizationRecommendation[] = [];

  constructor(private authService: AuthService, private api: MedicalStaffApiService) {}

  ngOnInit(): void {
    this.load();
  }

  metricWidth(metric: OptimizationMetric): number {
    if (metric.unit === '%') {
      return Math.min(100, metric.value);
    }
    return Math.min(100, metric.value * 10);
  }

  load(): void {
    const id = this.getPersonnelId();
    if (!id) {
      this.loading = false;
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.api.getOptimization(id).subscribe({
      next: (res) => {
        this.score = res.score || 0;
        this.metrics = res.metrics || [];
        this.recommendations = res.recommendations || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger le centre d\'optimisation.';
      }
    });
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; id_personnel?: number } | null;
    return user?.id ?? user?.id_personnel;
  }
}

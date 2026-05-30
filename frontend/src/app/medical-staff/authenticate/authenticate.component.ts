import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UserType } from '../../models/auth.model';

@Component({
  selector: 'app-authenticate',
  templateUrl: './authenticate.component.html',
  styleUrls: ['./authenticate.component.css']
})
export class AuthenticateComponent implements OnInit {
  accessCode: string = '';
  step: 'form' | 'loading' | 'success' = 'form';
  errorMessage: string = '';
  returnUrl: string = '';

  /** Expose step checks as getters for cleaner template. */
  get isLoading(): boolean { return this.step === 'loading'; }
  get isSuccess(): boolean { return this.step === 'success'; }

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Capture intended destination so we can redirect back after auth
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';

    // Already authenticated → skip straight to the correct workspace
    if (this.authService.isAuthenticated() && this.authService.isMedicalStaff()) {
      this.navigateToDashboard();
    }
  }

  authenticate(): void {
    this.errorMessage = '';

    if (!this.accessCode || !this.accessCode.trim()) {
      this.errorMessage = 'Le code d\'accès est obligatoire.';
      return;
    }

    this.step = 'loading';

    this.authService.login({
      userType: UserType.MEDICAL_STAFF,
      accessCode: this.accessCode.trim()
    }).subscribe({
      next: () => {
        this.step = 'success';
        // Brief success animation then navigate
        setTimeout(() => this.navigateToDashboard(), 1400);
      },
      error: (error) => {
        this.step = 'form';
        if (error.status === 0) {
          this.errorMessage = 'Serveur inaccessible. Vérifiez votre connexion.';
        } else if (error.status === 500) {
          this.errorMessage = 'Erreur serveur. Veuillez réessayer.';
        } else if (error.status === 401 || error.status === 400 || error.status === 404) {
          this.errorMessage = 'Code d\'accès invalide.';
        } else if (error.error?.message) {
          this.errorMessage = error.error.message;
        } else if (error.error?.error) {
          this.errorMessage = error.error.error;
        } else {
          this.errorMessage = 'Code d\'accès invalide ou erreur réseau.';
        }
      }
    });
  }

  /** Navigate to the correct workspace after successful authentication. */
  private navigateToDashboard(): void {
    // returnUrl takes priority (user was trying to reach a specific page)
    if (this.returnUrl && this.returnUrl !== '/medical-staff') {
      this.router.navigateByUrl(this.returnUrl);
      return;
    }

    // Determine default landing page by role
    if (this.authService.isNurse()) {
      this.router.navigate(['/medical-staff/nurse/dashboard']);
    } else {
      // Default: doctor → planning (primary work view)
      this.router.navigate(['/medical-staff/doctor/planning']);
    }
  }
}

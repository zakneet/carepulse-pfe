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
  isLoading: boolean = false;
  errorMessage: string = '';
  returnUrl: string = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/medical-staff/doctor/planning';
    
    // If already authenticated as medical staff, redirect
    if (this.authService.isAuthenticated() && this.authService.isMedicalStaff()) {
      this.router.navigateByUrl(this.returnUrl);
    }
  }

  authenticate(): void {
    this.errorMessage = '';
    
    if (!this.accessCode || this.accessCode.trim() === '') {
      this.errorMessage = 'Le code d\'accès est obligatoire.';
      return;
    }

    this.isLoading = true;

    this.authService.login({
      userType: UserType.MEDICAL_STAFF,
      accessCode: this.accessCode.trim()
    }).subscribe({
      next: () => {
        this.isLoading = false;
        const targetRoute = this.authService.getMedicalStaffBaseRoute() + '/dashboard';
        this.router.navigateByUrl(this.returnUrl ? this.returnUrl : targetRoute);
      },
      error: (error) => {
        this.isLoading = false;
        if (error.status === 0) {
          this.errorMessage = 'Serveur inaccessible. Veuillez vérifier votre connexion.';
        } else if (error.status === 500) {
          this.errorMessage = 'Erreur interne du serveur.';
        } else if (error.status === 401 || error.status === 400) {
          this.errorMessage = 'Code d\'accès incorrect.';
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
}

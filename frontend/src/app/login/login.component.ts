import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { LoginRequest, UserType } from '../models/auth.model';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  credentials = {
    telephone: '',
    password: '',
    accessCode: ''
  };
  selectedUserType: UserType = UserType.PATIENT;
  readonly UserType = UserType;

  isLoading = false;
  message = '';
  messageType: 'error' | 'success' = 'error';
  returnUrl = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';
  }

  login(): void {
    this.message = '';

    if (this.selectedUserType === UserType.MEDICAL_STAFF) {
      if (!this.credentials.accessCode) {
        this.message = 'Code d\'acces obligatoire pour le personnel medical.';
        this.messageType = 'error';
        return;
      }
    } else {
      if (!this.credentials.telephone || !this.credentials.password) {
        this.message = 'Numero de telephone et mot de passe sont obligatoires.';
        this.messageType = 'error';
        return;
      }
    }

    this.isLoading = true;

    const loginRequest: LoginRequest = this.selectedUserType === UserType.MEDICAL_STAFF
      ? {
          userType: UserType.MEDICAL_STAFF,
          accessCode: this.credentials.accessCode
        }
      : {
          telephone: this.credentials.telephone,
          password: this.credentials.password,
          userType: UserType.PATIENT
        };

    this.authService.login(loginRequest).subscribe({
      next: () => {
        this.isLoading = false;
        this.messageType = 'success';
        this.message = 'Connexion réussie !';
        this.redirectAfterLogin();
      },
      error: (error) => {
        this.isLoading = false;
        this.messageType = 'error';

        if (error.error?.error) {
          this.message = error.error.error;
        } else {
          this.message = 'Erreur de connexion. Vérifiez vos identifiants.';
        }
      }
    });
  }

  setUserType(type: UserType): void {
    this.selectedUserType = type;
    this.message = '';
  }

  private redirectAfterLogin(): void {
    const targetUrl = this.returnUrl || (this.selectedUserType === UserType.MEDICAL_STAFF
      ? this.authService.getMedicalStaffBaseRoute()
      : '/patient/dashboard');
    this.router.navigateByUrl(targetUrl);
  }
}

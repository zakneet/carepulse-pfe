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
  // Types d'utilisateurs disponibles
  userTypeOptions = [
    { value: UserType.PATIENT, label: 'Patient', group: 'patient' },
    { value: UserType.MEDICAL_STAFF, label: 'Personnel de santé', group: 'medical' }
  ];

  // Étape 1 = choix du profil, Étape 2 = saisie des identifiants
  currentStep: 1 | 2 = 1;
  selectedUserType: UserType | null = null;
  credentials = {
    email: '',
    password: '',
    accessCode: ''
  };

  message = '';
  messageType: 'error' | 'success' = 'error';
  showPassword = false;
  isLoading = false;
  returnUrl = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';
  }

  ngOnInit(): void {
    // On laisse la page de connexion accessible meme si un token existe,
    // pour eviter une redirection automatique inattendue.
  }

  /**
   * Vérifier si le type sélectionné est personnel médical
   */
  isMedicalStaffUserType(): boolean {
    return this.selectedUserType === UserType.MEDICAL_STAFF;
  }

  /**
   * Changer le type d'utilisateur
   */
  selectUserType(userType: UserType): void {
    this.selectedUserType = userType;
    this.currentStep = 2;
    this.message = '';
    this.credentials.accessCode = '';
  }

  backToStep1(): void {
    this.currentStep = 1;
    this.message = '';
  }

  /**
   * Basculer la visibilité du mot de passe
   */
  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  /**
   * Soumettre le formulaire de connexion
   */
  login(): void {
    this.message = '';

    if (!this.selectedUserType) {
      this.message = 'Veuillez choisir un profil: Patient ou Personnel de sante.';
      this.messageType = 'error';
      this.currentStep = 1;
      return;
    }

    const isMedical = this.isMedicalStaffUserType();

    if (isMedical) {
      if (!this.credentials.accessCode) {
        this.message = 'Le code d\'acces est obligatoire pour le personnel medical.';
        this.messageType = 'error';
        return;
      }
    } else {
      // Validation patient
      if (!this.credentials.email || !this.credentials.password) {
        this.message = 'Email et mot de passe sont obligatoires.';
        this.messageType = 'error';
        return;
      }
    }

    this.isLoading = true;

    const loginRequest: LoginRequest = {
      email: isMedical ? undefined : this.credentials.email,
      password: isMedical ? undefined : this.credentials.password,
      userType: this.selectedUserType,
      accessCode: this.credentials.accessCode || undefined
    };

    this.authService.login(loginRequest).subscribe({
      next: (user) => {
        this.isLoading = false;
        this.messageType = 'success';
        this.message = 'Connexion réussie !';

        // Redirection après succès
        setTimeout(() => {
          this.redirectToRoleDashboard();
        }, 500);
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

  /**
   * Redirection selon le rôle de l'utilisateur
   */
  private redirectToRoleDashboard(): void {
    const userRole = this.authService.getUserRole();

    if (this.returnUrl) {
      this.router.navigateByUrl(this.returnUrl);
    } else {
      switch (userRole) {
        case 'patient':
          this.router.navigate(['/patient/dashboard']);
          break;
        case 'medical_staff':
          this.router.navigate([this.authService.getMedicalStaffBaseRoute(), 'planning']);
          break;
        case 'admin':
          this.router.navigate(['/admin/dashboard']);
          break;
        default:
          this.router.navigate(['/']);
      }
    }
  }
} 

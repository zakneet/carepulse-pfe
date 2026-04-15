import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { AuthUser, AuthState, LoginRequest, LoginResponse, UserRole } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authState = new BehaviorSubject<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    userRole: null
  });

  public authState$ = this.authState.asObservable();

  constructor(private http: HttpClient) {
    this.loadAuthState(); // Charger l'état depuis localStorage au démarrage
  }

  /**
   * Charger l'état d'authentification depuis localStorage
   */
  private loadAuthState(): void {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('authUser');

    if (storedToken && storedUser) {
      try {
        const user = JSON.parse(storedUser);
        this.authState.next({
          isAuthenticated: true,
          user,
          token: storedToken,
          userRole: user.role
        });
      } catch (error) {
        console.error('Erreur chargement authState:', error);
        this.logout();
      }
    }
  }

  /**
   * Connexion utilisateur
   */
  login(credentials: LoginRequest): Observable<AuthUser> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/login`, credentials).pipe(
      tap((response: LoginResponse) => {
        // Stocker le token et l'utilisateur
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('authUser', JSON.stringify(response.user));

        // Mettre à jour l'état
        this.authState.next({
          isAuthenticated: true,
          user: response.user,
          token: response.token,
          userRole: response.user.role
        });
      }),
      map((response: LoginResponse) => response.user)
    );
  }

  /**
   * Déconnexion
   */
  logout(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    localStorage.removeItem('patientProfile'); // Nettoyer aussi les anciens données

    this.authState.next({
      isAuthenticated: false,
      user: null,
      token: null,
      userRole: null
    });
  }

  /**
   * Obtenir l'utilisateur actuel
   */
  getCurrentUser(): AuthUser | null {
    return this.authState.value.user;
  }

  /**
   * Obtenir le token JWT
   */
  getToken(): string | null {
    return this.authState.value.token;
  }

  /**
   * Vérifier si l'utilisateur est authentifié
   */
  isAuthenticated(): boolean {
    return this.authState.value.isAuthenticated;
  }

  /**
   * Obtenir le rôle de l'utilisateur actuel
   */
  getUserRole(): UserRole | null {
    return this.authState.value.userRole;
  }

  /**
   * Vérifier si l'utilisateur a un rôle spécifique
   */
  hasRole(role: UserRole): boolean {
    return this.authState.value.userRole === role;
  }

  /**
   * Vérifier si l'utilisateur est un patient
   */
  isPatient(): boolean {
    return this.hasRole(UserRole.PATIENT);
  }

  /**
   * Vérifier si l'utilisateur est personnel médical
   */
  isMedicalStaff(): boolean {
    return this.hasRole(UserRole.MEDICAL_STAFF);
  }

  isNurse(): boolean {
    const user = this.getCurrentUser();
    return this.isMedicalStaff() && user?.staffCategory === 'nurse';
  }

  isDoctor(): boolean {
    return this.isMedicalStaff() && !this.isNurse();
  }

  getMedicalStaffBaseRoute(): string {
    return this.isNurse() ? '/medical-staff/nurse' : '/medical-staff/doctor';
  }

  /**
   * Vérifier si l'utilisateur est administrateur
   */
  isAdmin(): boolean {
    return this.hasRole(UserRole.ADMIN);
  }
}

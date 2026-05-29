import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { AuthUser, AuthState, LoginRequest, LoginResponse, UserRole, UserType } from '../models/auth.model';

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
   * Charger l'état d'authentification depuis le stockage
   * Medical staff: sessionStorage (expire à la fermeture de l'onglet)
   * Patients: localStorage (persistant)
   */
  private loadAuthState(): void {
    // Try sessionStorage first (medical staff)
    let storedToken = sessionStorage.getItem('medAuthToken');
    let storedUser = sessionStorage.getItem('medAuthUser');
    
    // Fallback to localStorage (patients)
    if (!storedToken || !storedUser) {
      storedToken = localStorage.getItem('authToken');
      storedUser = localStorage.getItem('authUser');
    }

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
    const url = credentials.userType === UserType.MEDICAL_STAFF 
      ? `${environment.apiUrl}/medical-staff/authenticate` 
      : `${environment.apiUrl}/login`;
      
    const payload: any = { ...credentials };
    if (payload.accessCode) {
      payload.access_code = payload.accessCode;
    }
      
    return this.http.post<LoginResponse>(url, payload).pipe(
      tap((response: LoginResponse) => {
        console.log('[AuthService] Login response:', response);
        // Handle custom format for medical-staff authenticate endpoint
        const token = response.token || (response as any).token;
        const user = response.user || (response as any).doctor;
        
        if (user && !user.role) {
            user.role = UserRole.MEDICAL_STAFF;
            user.staffCategory = 'doctor';
        }
        
        if (user && (user as any).id_personnel && !user.id) {
            user.id = (user as any).id_personnel;
        }

        console.log('[AuthService] Mapped user:', user);

        const isMedicalStaff = credentials.userType === UserType.MEDICAL_STAFF;

        if (isMedicalStaff) {
          // Medical staff: sessionStorage only (clears on tab close → forces re-auth)
          sessionStorage.setItem('medAuthToken', token);
          sessionStorage.setItem('medAuthUser', JSON.stringify(user));
          // Also clear any old localStorage keys
          localStorage.removeItem('authToken');
          localStorage.removeItem('authUser');
        } else {
          // Patients: localStorage (persistent)
          localStorage.setItem('authToken', token);
          localStorage.setItem('authUser', JSON.stringify(user));
        }

        // Mettre à jour l'état
        this.authState.next({
          isAuthenticated: true,
          user: user as AuthUser,
          token: token,
          userRole: user.role
        });
      }),
      map((response: LoginResponse) => {
        const user = response.user || (response as any).doctor;
        if (user && (user as any).id_personnel && !user.id) {
            user.id = (user as any).id_personnel;
        }
        return user as AuthUser;
      })
    );
  }

  /**
   * Déconnexion
   */
  logout(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    localStorage.removeItem('patientProfile');
    // Clear medical staff session
    sessionStorage.removeItem('medAuthToken');
    sessionStorage.removeItem('medAuthUser');

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

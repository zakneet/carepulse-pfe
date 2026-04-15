/**
 * Modèles et interfaces pour l'authentification et les utilisateurs
 */

export enum UserRole {
  PATIENT = 'patient',
  MEDICAL_STAFF = 'medical_staff',
  ADMIN = 'admin'
}

export enum UserType {
  PATIENT = 'patient',
  MEDICAL_STAFF = 'medical_staff',
  ADMIN = 'admin'
}

export interface LoginRequest {
  email?: string;
  password?: string;
  userType: UserType; // patient, medical_staff, admin
  accessCode?: string; // Requis si userType = medical_staff
}

export interface LoginResponse {
  message: string;
  user: AuthUser;
  token: string; // JWT token
}

export interface AuthUser {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  role: UserRole; // patient, medical_staff, admin
  userType?: UserType; // spécifique pour medical_staff
  specialite?: string;
  staffCategory?: 'doctor' | 'nurse';
}

export interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  token: string | null;
  userRole: UserRole | null;
}

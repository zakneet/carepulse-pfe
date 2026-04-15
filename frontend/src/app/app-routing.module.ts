import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { RdvFormComponent } from './rdv-form/rdv-form.component';
import { RdvListComponent } from './rdv-list/rdv-list.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { PatientComponent } from './patient/patient.component';
import { PatientPublicComponent } from './patient-public/patient-public.component';
import { MedicalStaffDashboardComponent } from './medical-staff/components/dashboard/medical-staff-dashboard.component';
import { MedicalStaffAppointmentsComponent } from './medical-staff/components/appointments/medical-staff-appointments.component';
import { MedicalStaffPatientsComponent } from './medical-staff/components/patients/medical-staff-patients.component';
import { MedicalStaffFormComponent } from './medical-staff/components/form/medical-staff-form.component';
import { MedicalStaffPatientProfileComponent } from './medical-staff/components/patient-profile/medical-staff-patient-profile.component';

import { AuthGuard } from './guards/auth.guard';
import { RoleGuard } from './guards/role.guard';
import { UserRole } from './models/auth.model';

const routes: Routes = [
  // Routes publiques
  { path: 'home', component: HomeComponent },
  { path: 'patient', component: PatientPublicComponent, pathMatch: 'full' },
  { path: 'patient/booking', component: RdvFormComponent },
  { path: 'patient/rdv/new', component: RdvFormComponent },
  { path: 'rdv', component: RdvFormComponent },
  { path: 'rdv/new', component: RdvFormComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },

  // Redirection explicite vers le planning du medecin (par defaut)
  { path: 'medical-staff', redirectTo: '/medical-staff/doctor/planning', pathMatch: 'full' },

  // Route par défaut
  {
    path: 'medical-staff',
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: [UserRole.MEDICAL_STAFF] },
    children: [
      { path: '', redirectTo: 'doctor/planning', pathMatch: 'full' },
      { path: 'doctor', redirectTo: 'doctor/planning', pathMatch: 'full' },
      { path: 'doctor/form', component: MedicalStaffFormComponent, data: { staffView: 'doctor' } },
      { path: 'doctor/planning', component: MedicalStaffDashboardComponent, data: { staffView: 'doctor' } },
      { path: 'doctor/dashboard', component: MedicalStaffDashboardComponent, data: { staffView: 'doctor' } },
      { path: 'doctor/appointments', component: MedicalStaffAppointmentsComponent, data: { staffView: 'doctor' } },
      { path: 'doctor/patients', component: MedicalStaffPatientsComponent, data: { staffView: 'doctor' } },
      { path: 'doctor/patient-profile/:idPatient', component: MedicalStaffPatientProfileComponent, data: { staffView: 'doctor', profileEditable: true } },

      { path: 'nurse', redirectTo: 'nurse/planning', pathMatch: 'full' },
      { path: 'nurse/form', component: MedicalStaffFormComponent, data: { staffView: 'nurse' } },
      { path: 'nurse/planning', component: MedicalStaffDashboardComponent, data: { staffView: 'nurse' } },
      { path: 'nurse/dashboard', component: MedicalStaffDashboardComponent, data: { staffView: 'nurse' } },
      { path: 'nurse/appointments', component: MedicalStaffAppointmentsComponent, data: { staffView: 'nurse' } },
      { path: 'nurse/patients', component: MedicalStaffPatientsComponent, data: { staffView: 'nurse' } },
      { path: 'nurse/patient-profile/:idPatient', component: MedicalStaffPatientProfileComponent, data: { staffView: 'nurse', profileEditable: false } },

      // Routes heritagees (compatibilite)
      { path: 'form', redirectTo: 'doctor/form', pathMatch: 'full' },
      { path: 'planning', redirectTo: 'doctor/planning', pathMatch: 'full' },
      { path: 'dashboard', redirectTo: 'doctor/dashboard', pathMatch: 'full' },
      { path: 'appointments', redirectTo: 'doctor/appointments', pathMatch: 'full' },
      { path: 'patients', redirectTo: 'doctor/patients', pathMatch: 'full' },
      { path: 'patient-profile/:idPatient', redirectTo: 'doctor/patient-profile/:idPatient', pathMatch: 'full' }
    ]
  },
  // Routes protégées pour patients
  {
    path: 'patient',
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: [UserRole.PATIENT] },
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'consultations', component: PatientComponent },
      { path: 'rdvs', component: RdvListComponent },
      { path: 'booking', component: RdvFormComponent },
      { path: 'rdv/new', component: RdvFormComponent },
      { path: 'profile', component: ProfileComponent },

    ]
  },

  // Routes personnel médical (directes, séparées du patient)


  // Routes héritées (à adapter)
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
  { path: 'rdvs', component: RdvListComponent, canActivate: [AuthGuard] },
  { path: '', redirectTo: '/home', pathMatch: 'full' },

  // Wildcard - rediriger vers login
  { path: '**', redirectTo: '/home' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

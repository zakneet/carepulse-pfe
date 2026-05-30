import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { RdvFormComponent } from './rdv-form/rdv-form.component';
import { RdvListComponent } from './rdv-list/rdv-list.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { PatientComponent } from './patient/patient.component';
import { HomeComponent } from './home/home.component';
import { MedicalStaffDashboardComponent } from './medical-staff/components/dashboard/medical-staff-dashboard.component';
import { MedicalStaffAppointmentsComponent } from './medical-staff/components/appointments/medical-staff-appointments.component';
import { MedicalStaffPatientsComponent } from './medical-staff/components/patients/medical-staff-patients.component';
import { MedicalStaffFormComponent } from './medical-staff/components/form/medical-staff-form.component';
import { MedicalStaffPatientProfileComponent } from './medical-staff/components/patient-profile/medical-staff-patient-profile.component';
import { DoctorsComponent } from './doctors/doctors.component';
import { BookingComponent } from './booking/booking.component';
import { AuthenticateComponent } from './medical-staff/authenticate/authenticate.component';
import { AuthGuard } from './guards/auth.guard';
import { PlanningComponent } from './medical-staff/components/planning/planning.component';
import { WaitingListComponent } from './medical-staff/components/waiting-list/waiting-list.component';
import { OptimizationComponent } from './medical-staff/components/optimization/optimization.component';
import { AnalyticsComponent } from './medical-staff/components/analytics/analytics.component';
import { NotificationsComponent } from './medical-staff/components/notifications/notifications.component';
import { SettingsComponent } from './medical-staff/components/settings/settings.component';

const medicalStaffChildren: Routes = [
  // ── REDIRECTS (no canActivate — Angular forbids it on redirectTo) ─────────────
  // The PARENT route has canActivate:[AuthGuard] which fires before any child resolves.
  { path: '', redirectTo: 'doctor/dashboard', pathMatch: 'full' },
  { path: 'doctor', redirectTo: 'doctor/dashboard', pathMatch: 'full' },
  { path: 'doctor/optimized-calendar', redirectTo: 'doctor/planning', pathMatch: 'full' },
  { path: 'nurse', redirectTo: 'nurse/dashboard', pathMatch: 'full' },

  // ── DOCTOR routes ─────────────────────────────────────────────────────────────
  { path: 'doctor/planning',          component: PlanningComponent,                  data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/planning-full',     component: PlanningComponent,                  data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/dashboard',         component: MedicalStaffDashboardComponent,     data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/appointments',      component: MedicalStaffAppointmentsComponent,  data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/patients',          component: MedicalStaffPatientsComponent,      data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/form',              component: MedicalStaffFormComponent,          data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/patient-profile/:idPatient', component: MedicalStaffPatientProfileComponent, data: { staffView: 'doctor', profileEditable: true }, canActivate: [AuthGuard] },
  { path: 'doctor/waiting-list',      component: WaitingListComponent,               data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/optimization',      component: OptimizationComponent,              data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/analytics',         component: AnalyticsComponent,                 data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/notifications',     component: NotificationsComponent,             data: { staffView: 'doctor' }, canActivate: [AuthGuard] },
  { path: 'doctor/settings',          component: SettingsComponent,                  data: { staffView: 'doctor' }, canActivate: [AuthGuard] },

  // ── NURSE routes ──────────────────────────────────────────────────────────────
  { path: 'nurse/planning',           component: PlanningComponent,                  data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/planning-full',      component: PlanningComponent,                  data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/dashboard',          component: MedicalStaffDashboardComponent,     data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/appointments',       component: MedicalStaffAppointmentsComponent,  data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/patients',           component: MedicalStaffPatientsComponent,      data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/form',               component: MedicalStaffFormComponent,          data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/patient-profile/:idPatient', component: MedicalStaffPatientProfileComponent, data: { staffView: 'nurse', profileEditable: false }, canActivate: [AuthGuard] },
  { path: 'nurse/waiting-list',       component: WaitingListComponent,               data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/optimization',       component: OptimizationComponent,              data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/analytics',          component: AnalyticsComponent,                 data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/notifications',      component: NotificationsComponent,             data: { staffView: 'nurse' }, canActivate: [AuthGuard] },
  { path: 'nurse/settings',           component: SettingsComponent,                  data: { staffView: 'nurse' }, canActivate: [AuthGuard] },

  // ── Legacy alias redirects (target routes are already protected) ──────────────
  { path: 'form',        redirectTo: 'doctor/form',        pathMatch: 'full' },
  { path: 'planning',    redirectTo: 'doctor/planning',    pathMatch: 'full' },
  { path: 'dashboard',   redirectTo: 'doctor/dashboard',   pathMatch: 'full' },
  { path: 'appointments',redirectTo: 'doctor/appointments',pathMatch: 'full' },
  { path: 'patients',    redirectTo: 'doctor/patients',    pathMatch: 'full' },
  { path: 'patient-profile/:idPatient', redirectTo: 'doctor/patient-profile/:idPatient', pathMatch: 'full' }
];

const routes: Routes = [
  // Routes publiques
  { path: 'home', component: HomeComponent },
  { path: 'doctors', component: DoctorsComponent },
  { path: 'booking/:id', component: BookingComponent },
  { path: 'demo/rdvs', component: RdvListComponent },
  { path: 'patient/booking', component: BookingComponent },
  { path: 'patient/rdv/new', component: BookingComponent },
  { path: 'rdv', component: BookingComponent },
  { path: 'rdv/new', component: BookingComponent },
  { path: 'patient/login', redirectTo: '/home', pathMatch: 'full' },
  { path: 'login', redirectTo: '/home', pathMatch: 'full' },
  { path: 'register', redirectTo: '/home', pathMatch: 'full' },

  { path: 'medicalstuff', redirectTo: '/medical-staff', pathMatch: 'prefix' },
  { path: 'medical-staff/authenticate', component: AuthenticateComponent },
  { path: 'medical-staff', children: medicalStaffChildren, canActivate: [AuthGuard] },

  // Route par défaut
  {
    path: 'patient',
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

  // Routes héritées (à adapter)
  { path: 'dashboard', component: DashboardComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'rdvs', component: RdvListComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },

  // Wildcard - rediriger vers accueil
  { path: '**', redirectTo: '/home' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

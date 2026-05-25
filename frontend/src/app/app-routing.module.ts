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

const medicalStaffChildren: Routes = [
  { path: '', redirectTo: 'doctor/planning', pathMatch: 'full' },
  { path: 'doctor', redirectTo: 'doctor/planning', pathMatch: 'full' },
  { path: 'doctor/form', component: MedicalStaffFormComponent, data: { staffView: 'doctor' } },
  { path: 'doctor/planning', component: MedicalStaffDashboardComponent, data: { staffView: 'doctor' } },
  { path: 'doctor/optimized-calendar', redirectTo: 'doctor/planning', pathMatch: 'full' },
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
];

const routes: Routes = [
  // Routes publiques
  { path: 'home', component: HomeComponent },
  { path: 'demo/rdvs', component: RdvListComponent },
  { path: 'patient/booking', component: RdvFormComponent },
  { path: 'patient/rdv/new', component: RdvFormComponent },
  { path: 'rdv', component: RdvFormComponent },
  { path: 'rdv/new', component: RdvFormComponent },
  { path: 'patient/login', redirectTo: '/home', pathMatch: 'full' },
  { path: 'login', redirectTo: '/home', pathMatch: 'full' },
  { path: 'register', redirectTo: '/home', pathMatch: 'full' },

  { path: 'medicalstuff', redirectTo: '/medical-staff', pathMatch: 'prefix' },
  { path: 'medical-staff', children: medicalStaffChildren },

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

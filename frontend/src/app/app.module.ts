import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';

import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FullCalendarModule } from '@fullcalendar/angular';

// Routing
import { AppRoutingModule } from './app-routing.module';

// Interceptors
import { JwtInterceptor } from './interceptors/jwt.interceptor';

// Components
import { AppComponent } from './app.component';
import { HeaderComponent } from './header/header.component';
import { PatientComponent } from './patient/patient.component';
import { RdvListComponent } from './rdv-list/rdv-list.component';
import { RdvFormComponent } from './rdv-form/rdv-form.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DemandeRdvComponent } from './demande-rdv/demande-rdv.component';
import { CreneauxComponent } from './creneaux/creneaux.component';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { PatientPublicComponent } from './patient-public/patient-public.component';
import { MedicalStaffDashboardComponent } from './medical-staff/components/dashboard/medical-staff-dashboard.component';
import { MedicalStaffAppointmentsComponent } from './medical-staff/components/appointments/medical-staff-appointments.component';
import { MedicalStaffPatientsComponent } from './medical-staff/components/patients/medical-staff-patients.component';
import { MedicalStaffFormComponent } from './medical-staff/components/form/medical-staff-form.component';
import { MedicalStaffPatientProfileComponent } from './medical-staff/components/patient-profile/medical-staff-patient-profile.component';
import { OptimizedCalendarComponent } from './optimized-calendar/optimized-calendar.component';
import { NotificationToastComponent } from './shared/notification-toast/notification-toast.component';
import { DoctorsComponent } from './doctors/doctors.component';
import { BookingComponent } from './booking/booking.component';
import { DoctorHeaderComponent } from './patient-dashboard/components/doctor-header/doctor-header.component';
import { AppointmentSuggestionComponent } from './patient-dashboard/components/appointment-suggestion/appointment-suggestion.component';
import { AppointmentHistoryComponent } from './patient-dashboard/components/appointment-history/appointment-history.component';
import { LiveTrackingComponent } from './patient-dashboard/components/live-tracking/live-tracking.component';
import { WeatherWidgetComponent } from './patient-dashboard/components/weather-widget/weather-widget.component';
import { TrafficWidgetComponent } from './patient-dashboard/components/traffic-widget/traffic-widget.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    PatientComponent,
    RdvListComponent,
    RdvFormComponent,
    LoginComponent,
    RegisterComponent,
    DemandeRdvComponent,
    CreneauxComponent,
    HomeComponent,
    DashboardComponent,
    ProfileComponent,
    PatientPublicComponent,
    MedicalStaffDashboardComponent,
    MedicalStaffFormComponent,
    MedicalStaffAppointmentsComponent,
    MedicalStaffPatientsComponent,
    MedicalStaffPatientProfileComponent,
    OptimizedCalendarComponent,
    NotificationToastComponent,
    DoctorsComponent,
    BookingComponent,
    DoctorHeaderComponent,
    AppointmentSuggestionComponent,
    AppointmentHistoryComponent,
    LiveTrackingComponent,
    WeatherWidgetComponent,
    TrafficWidgetComponent
  ],
  imports: [
    BrowserModule,
    CommonModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    FullCalendarModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: JwtInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserRole } from 'src/app/models/auth.model';
import { AuthService } from 'src/app/services/auth.service';
import { EmergencyEventsService, EmergencyType } from 'src/app/services/emergency-events.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  selectedEmergencyType: 'doctor-left-short' | 'doctor-left-long' | 'patient-on-site' | null = null;

  constructor(
    private emergencyEvents: EmergencyEventsService,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  activateEmergency(type: EmergencyType): void {
    this.selectedEmergencyType = type;
    this.emergencyEvents.trigger(type);

    if (type === 'patient-on-site' && this.authService.getUserRole() === UserRole.MEDICAL_STAFF) {
      setTimeout(() => {
        this.router.navigate([this.authService.getMedicalStaffBaseRoute(), 'form'], {
          queryParams: {
            mode: 'emergency',
            source: 'patient-on-site',
            ts: Date.now()
          }
        });
      }, 180);
    }
  }

}

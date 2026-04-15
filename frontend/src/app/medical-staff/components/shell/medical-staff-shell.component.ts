import { Component } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-medical-staff-shell',
  templateUrl: './medical-staff-shell.component.html',
  styleUrls: ['./medical-staff-shell.component.css']
})
export class MedicalStaffShellComponent {
  constructor(private authService: AuthService) {}

  logout(): void {
    this.authService.logout();
  }
}

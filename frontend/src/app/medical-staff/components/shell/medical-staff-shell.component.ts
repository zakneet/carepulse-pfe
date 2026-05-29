import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-medical-staff-shell',
  templateUrl: './medical-staff-shell.component.html',
  styleUrls: ['./medical-staff-shell.component.css']
})
export class MedicalStaffShellComponent implements OnInit {
  currentDoctor = 'Médecin';

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    const user = this.authService.getCurrentUser();
    if (user) {
      this.currentDoctor = `${user.prenom || ''} ${user.nom || ''}`.trim() || 'Médecin';
    }
  }

  logout(): void {
    // Clear session completely so access code is always re-required
    this.authService.logout();
    this.router.navigate(['/medical-staff/authenticate']);
  }
}

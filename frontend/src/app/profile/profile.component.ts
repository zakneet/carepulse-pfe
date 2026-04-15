import { Component, OnInit } from '@angular/core';

interface PatientProfile {
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
}

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profile: PatientProfile = {};

  ngOnInit(): void {
    const stored = localStorage.getItem('patientProfile');
    if (stored) {
      try {
        this.profile = JSON.parse(stored) as PatientProfile;
      } catch {
        this.profile = {};
      }
    }
  }
}

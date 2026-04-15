import { Component, OnInit } from '@angular/core';

type PatientProfile = {
  id?: number;
  nom?: string;
  prenom?: string;
  email?: string;
  role?: number;
  photoUrl?: string;
};

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  profile: PatientProfile | null = null;
  displayName = 'Invité';
  displayEmail = '';
  initials = '??';
  statusLabel = 'Patient';

  ngOnInit(): void {
    this.loadProfile();
  }

  private loadProfile(): void {
    const raw = localStorage.getItem('patientProfile');
    if (!raw) {
      this.applyProfile(null);
      return;
    }

    try {
      const parsed = JSON.parse(raw) as PatientProfile;
      this.applyProfile(parsed);
    } catch {
      this.applyProfile(null);
    }
  }

  private applyProfile(profile: PatientProfile | null): void {
    this.profile = profile;

    const prenom = (profile?.prenom || '').trim();
    const nom = (profile?.nom || '').trim();
    const fullName = `${prenom} ${nom}`.trim();
    this.displayName = fullName || 'Invité';
    this.displayEmail = (profile?.email || '').trim();

    const firstInitial = (prenom[0] || '').toUpperCase();
    const lastInitial = (nom[0] || '').toUpperCase();
    this.initials = (firstInitial + lastInitial) || '??';

    const role = profile?.role;
    if (role === 2) {
      this.statusLabel = 'Personnel';
    } else if (role === 9) {
      this.statusLabel = 'Admin';
    } else {
      this.statusLabel = 'Patient';
    }
  }
}

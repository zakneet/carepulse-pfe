import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { MedicalStaffApiService, WaitingListMatch } from '../../services/medical-staff-api.service';

@Component({
  selector: 'app-waiting-list',
  templateUrl: './waiting-list.component.html',
  styleUrls: ['./waiting-list.component.css']
})
export class WaitingListComponent implements OnInit {
  loading = true;
  errorMessage = '';
  freedSlots = 0;
  matches: WaitingListMatch[] = [];

  private readonly avatarColors = [
    'linear-gradient(135deg,#0284c7,#38bdf8)',
    'linear-gradient(135deg,#7c3aed,#a78bfa)',
    'linear-gradient(135deg,#059669,#34d399)',
    'linear-gradient(135deg,#d97706,#fbbf24)',
    'linear-gradient(135deg,#dc2626,#f87171)',
    'linear-gradient(135deg,#0891b2,#22d3ee)',
  ];

  constructor(private authService: AuthService, private api: MedicalStaffApiService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    const id = this.getPersonnelId();
    if (!id) {
      this.loading = false;
      this.errorMessage = 'Utilisateur medical non identifie.';
      return;
    }

    this.loading = true;
    this.api.getWaitingList(id).subscribe({
      next: (res) => {
        this.matches = res.matches || [];
        this.freedSlots = res.freeSlotsToday || 0;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger la liste d\'attente.';
      }
    });
  }

  getInitials(name: string): string {
    return (name || '?').split(' ').filter(Boolean).map((p) => p[0]).join('').slice(0, 2).toUpperCase();
  }

  getAvatarColor(index: number): string {
    return this.avatarColors[index % this.avatarColors.length];
  }

  getPriorityClass(priority: string): string {
    switch (priority) {
      case 'High': return 'wl-priority--high';
      case 'Moderate': return 'wl-priority--moderate';
      default: return 'wl-priority--low';
    }
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; id_personnel?: number } | null;
    return user?.id ?? user?.id_personnel;
  }
}

import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { MedicalStaffApiService, StaffNotification } from '../../services/medical-staff-api.service';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
  loading = true;
  errorMessage = '';
  filter = 'All';
  notifications: StaffNotification[] = [];

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
    this.api.getNotifications(id).subscribe({
      next: (res) => {
        this.notifications = res.notifications || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Impossible de charger les notifications.';
      }
    });
  }

  get filteredNotifications(): StaffNotification[] {
    if (this.filter === 'All') return this.notifications;
    const map: Record<string, string[]> = {
      Urgent: ['emergency'],
      System: ['info', 'system'],
      AI: ['ai', 'match']
    };
    const types = map[this.filter] || [];
    return this.notifications.filter((n) => types.includes(n.type));
  }

  getTypeClass(type: string): string {
    switch (type) {
      case 'emergency': return 'notif--emergency';
      case 'ai': return 'notif--ai';
      case 'match': return 'notif--match';
      default: return 'notif--info';
    }
  }

  markAllRead(): void {
    this.notifications.forEach((n) => { n.read = true; });
  }

  private getPersonnelId(): number | undefined {
    const user = this.authService.getCurrentUser() as { id?: number; id_personnel?: number } | null;
    return user?.id ?? user?.id_personnel;
  }
}

import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Observable } from 'rxjs';
import { AppNotification, NotificationService } from 'src/app/services/notification.service';

@Component({
  selector: 'app-notification-toast',
  templateUrl: './notification-toast.component.html',
  styleUrls: ['./notification-toast.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class NotificationToastComponent {
  notifications$: Observable<AppNotification[]> = this.notificationService.notifications$;

  constructor(private notificationService: NotificationService) {}

  dismiss(id: number): void {
    this.notificationService.dismiss(id);
  }
}

import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type NotificationType = 'success' | 'error' | 'info';

export interface AppNotification {
  id: number;
  type: NotificationType;
  message: string;
  durationMs: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private readonly notificationsSubject = new BehaviorSubject<AppNotification[]>([]);
  private nextId = 1;

  readonly notifications$ = this.notificationsSubject.asObservable();

  success(message: string): void {
    this.push('success', message, 3200);
  }

  error(message: string): void {
    this.push('error', message, 4200);
  }

  info(message: string): void {
    this.push('info', message, 3000);
  }

  dismiss(id: number): void {
    const current = this.notificationsSubject.getValue();
    this.notificationsSubject.next(current.filter((item) => item.id !== id));
  }

  private push(type: NotificationType, message: string, durationMs: number): void {
    const safeMessage = String(message || '').trim();
    if (!safeMessage) {
      return;
    }

    const current = this.notificationsSubject.getValue();
    const duplicate = current.some((item) => item.type === type && item.message === safeMessage);
    if (duplicate) {
      return;
    }

    const notification: AppNotification = {
      id: this.nextId++,
      type,
      message: safeMessage,
      durationMs,
    };

    this.notificationsSubject.next([...current, notification]);
    window.setTimeout(() => this.dismiss(notification.id), notification.durationMs);
  }
}

import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject, Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: Socket | null = null;
  private readonly connectionStateSubject = new BehaviorSubject<boolean>(false);
  private readonly cabinetStatusSubject = new Subject<any>();

  connectionState$ = this.connectionStateSubject.asObservable();

  connect(): void {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(environment.apiUrl, {
      transports: ['websocket', 'polling'],
      autoConnect: true
    });

    this.socket.on('connect', () => {
      this.connectionStateSubject.next(true);
    });

    this.socket.on('disconnect', () => {
      this.connectionStateSubject.next(false);
    });

    this.socket.on('connect_error', () => {
      this.connectionStateSubject.next(false);
    });

    // Listen for cabinet status updates
    this.socket.on('cabinet_status_update', (data: any) => {
      this.cabinetStatusSubject.next(data);
    });
  }

  onCabinetStatusUpdate(): Observable<any> {
    return this.cabinetStatusSubject.asObservable();
  }

  onEvent(event: string): Observable<any> {
    return new Observable(observer => {
      if (!this.socket) {
        this.connect();
      }
      this.socket?.on(event, (data: any) => {
        observer.next(data);
      });
    });
  }

  requestCabinetStatus(): void {
    if (!this.socket?.connected) {
      return;
    }
    this.socket.emit('request_cabinet_status');
  }

  sendMessage(message: string): void {
    if (!this.socket?.connected) {
      return;
    }

    this.socket.send(message);
  }

  joinRoom(event: string, payload?: any): void {
     if (!this.socket?.connected) {
       this.connect();
     }
     this.socket?.emit(event, payload || {});
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
    this.connectionStateSubject.next(false);
  }
}
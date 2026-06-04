import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import {
  PatientPortalData,
  PatientPortalService,
  PortalDocument
} from './patient-portal.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-patient-portal',
  templateUrl: './patient-portal.component.html',
  styleUrls: ['./patient-portal.component.css']
})
export class PatientPortalComponent implements OnInit {
  loading = true;
  errorMessage = '';
  data: PatientPortalData | null = null;
  activeSection: 'dashboard' | 'appointments' | 'documents' | 'notifications' = 'dashboard';
  selectedDoc: { title: string; content: string } | null = null;
  weather: { temp?: number; description?: string; city?: string } | null = null;
  deferredPrompt: any = null;
  showInstallHelpModal = false;

  // Real-time tracking
  isTrackingActive = false;
  timeRemaining = '';
  trackingInterval: any;

  @HostListener('window:beforeinstallprompt', ['$event'])
  onbeforeinstallprompt(e: Event) {
    e.preventDefault();
    this.deferredPrompt = e;
  }

  installApp() {
    if (!this.deferredPrompt) {
      // Native prompt unavailable: show manual instructions
      this.showInstallHelpModal = true;
      return;
    }
    
    this.deferredPrompt.prompt();
    this.deferredPrompt.userChoice.then((choiceResult: any) => {
      this.deferredPrompt = null;
    });
  }

  dismissInstallHelp() {
    this.showInstallHelpModal = false;
  }

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private portalService: PatientPortalService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const token = params.get('token') || '';
      if (!token) {
        this.errorMessage = 'Lien invalide.';
        this.loading = false;
        return;
      }
      this.loadPortal(token);
    });
  }

  ngOnDestroy(): void {
    if (this.trackingInterval) clearInterval(this.trackingInterval);
  }

  startTrackingInterval(): void {
    if (this.trackingInterval) clearInterval(this.trackingInterval);
    
    this.updateTrackingStatus(); // Initial check
    this.trackingInterval = setInterval(() => {
      this.updateTrackingStatus();
    }, 60000);
  }

  updateTrackingStatus(): void {
    if (!this.data || !this.data.upcomingAppointments || this.data.upcomingAppointments.length === 0) {
      this.isTrackingActive = false;
      return;
    }

    const nxt = this.data.upcomingAppointments[0];
    const appointmentTime = new Date(`${nxt.dateRDV}T${nxt.heureDebut}:00`).getTime();
    const now = Date.now();
    const diff = appointmentTime - now;

    if (diff > 0 && diff <= 2 * 60 * 60 * 1000) {
      this.isTrackingActive = true;
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      this.timeRemaining = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    } else {
      this.isTrackingActive = false;
      this.timeRemaining = '';
    }
  }

  loadPortal(token: string): void {
    this.loading = true;
    this.errorMessage = '';
    this.portalService.getPortal(token).subscribe({
      next: (res) => {
        this.data = res;
        this.loading = false;
        
        // Save secure path for PWA auto-redirect
        const fullPath = window.location.pathname + window.location.search + window.location.hash;
        localStorage.setItem('opticlinic_last_patient_portal_path', fullPath);

        this.loadWeather(res.clinic?.address || 'Tunis');
        this.startTrackingInterval();
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.error || 'Impossible d\'accéder à votre espace patient.';
      }
    });
  }

  private loadWeather(location: string): void {
    const city = (location.split(',')[0] || 'Tunis').trim();
    this.http.get<any>(`${environment.apiUrl}/weather?city=${encodeURIComponent(city)}`).subscribe({
      next: (res) => {
        const cw = res?.current_weather || res?.currentWeather || {};
        this.weather = {
          temp: cw.temperature ?? cw.temp,
          description: cw.weathercode ? 'Ensoleillé' : (res?.weather_recommendation || '—'),
          city
        };
      },
      error: () => {
        this.weather = { city, description: 'Météo indisponible' };
      }
    });
  }

  openDocument(doc: PortalDocument): void {
    if (!this.data?.token) return;
    this.portalService.getDocument(this.data.token, doc.id).subscribe({
      next: (res) => {
        this.selectedDoc = { title: res.title, content: res.content };
      }
    });
  }

  closeDocument(): void {
    this.selectedDoc = null;
  }

  downloadDocument(): void {
    if (!this.selectedDoc) return;
    const blob = new Blob([this.selectedDoc.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.selectedDoc.title.replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  get mapUrl(): string {
    const q = encodeURIComponent(this.data?.clinic?.mapQuery || 'OptiClinic Tunis');
    return `https://www.google.com/maps/search/?api=1&query=${q}`;
  }

  get unreadNotifications(): number {
    return (this.data?.notifications || []).filter((n) => !n.read).length;
  }

  rebookAppointment(): void {
    if (!this.data || !this.data.doctor || !this.data.token) return;
    this.router.navigate(['/patient/booking'], {
      queryParams: {
        doctorId: this.data.doctor.idPersonnel || this.data.doctor.id,
        fromPortal: 'true',
        portalToken: this.data.token
      }
    });
  }
}

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
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

  constructor(
    private route: ActivatedRoute,
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

  loadPortal(token: string): void {
    this.loading = true;
    this.errorMessage = '';
    this.portalService.getPortal(token).subscribe({
      next: (res) => {
        this.data = res;
        this.loading = false;
        this.loadWeather(res.clinic?.address || 'Tunis');
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
}

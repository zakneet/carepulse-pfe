import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { SocketService } from '../services/socket.service';
import { environment } from 'src/environments/environment';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

type PatientProfile = {
  patient: {
    id: number;
    nom: string;
    prenom: string;
    email: string;
    telephone: string;
    cin: string;
    adresse?: string;
    dateNaissance: string;
    age: number;
    sexe: string;
  };
  allergies: string[];
  maladies: string[];
  historiqueMedical: string;
  appointments: Array<{
    id: number;
    dateRDV: string;
    heureDebut: string;
    heureFin: string;
    motifConsultation: string;
    statut: string;
    location?: string;
    medecin?: string;
    medecinNom?: string;
    medecinPrenom?: string;
    specialite?: string;
    latitude?: number;
    longitude?: number;
  }>;
};

type TravelNotice = {
  status: string;
  message?: string;
  recommendation?: string;
  duration_normal?: number | null;
  duration_current?: number | null;
  traffic_delay_minutes?: number | null;
  traffic_delay_percent?: number | null;
  traffic_level?: 'fluide' | 'moyen' | 'dense' | 'unknown';
  departure_time?: string | null;
  weather_recommendation?: string | null;
  weather_is_bad?: boolean;
  should_notify?: boolean;
  notification_title?: string;
  notification_body?: string;
  checked_at?: string;
};

type TravelNoticesResponse = {
  patientId: number;
  patientAddress: string;
  clinicAddress: string;
  notices: Array<{
    rdvId: number;
    appointmentDate?: string | null;
    appointmentTime?: string | null;
    notice: TravelNotice;
  }>;
};

type TravelNoticeState = {
  loading: boolean;
  notice: TravelNotice | null;
  error: string | null;
};

type CabinetStatus = {
  isOpen: boolean;
  doctorAvailable: boolean;
  waitTime: number;
  totalPatients: number;
  message: string;
};

@Component({
  selector: 'app-patient',
  templateUrl: './patient.component.html',
  styleUrls: ['./patient.component.css']
})
export class PatientComponent implements OnInit, OnDestroy {
  private readonly apiUrl = environment.apiUrl;
  private destroy$ = new Subject<void>();
  private travelRefreshTimer?: ReturnType<typeof setInterval>;
  private readonly travelAlertPrefix = 'travel-alert:';

  profile: PatientProfile | null = null;
  isLoading = true;
  errorMessage = '';
  isRdvListExpanded = false;
  isTrackingModalOpen = false;
  selectedRdvForTracking: any = null;
  cabinetStatus: CabinetStatus | null = null;
  isTracking = false;
  patientAddress = '';
  addressMessage = '';
  addressSaving = false;
  travelNotificationsEnabled = false;
  travelNoticeMap: Record<number, TravelNoticeState> = {};
  // weather state per appointment key
  weatherMap: Record<string, { loading: boolean; temperature?: number; windspeed?: number; recommendation?: string | null }> = {};

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router,
    private socketService: SocketService
  ) {}

  ngOnInit(): void {
    this.loadProfile();
    this.socketService.connect();
    this.startTravelRefreshLoop();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.travelRefreshTimer) {
      clearInterval(this.travelRefreshTimer);
    }
  }

  getPatientInitials(): string {
    if (!this.profile?.patient) {
      return 'P';
    }

    const first = (this.profile.patient.prenom || '').trim().charAt(0);
    const last = (this.profile.patient.nom || '').trim().charAt(0);
    return `${first || 'P'}${last || ''}`.toUpperCase();
  }

  getPatientFullName(): string {
    if (!this.profile?.patient) {
      return 'Patient';
    }

    return `${this.profile.patient.prenom || ''} ${this.profile.patient.nom || ''}`.trim() || 'Patient';
  }

  private loadProfile(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.http.get<PatientProfile>(this.apiUrl + '/patient/profile').subscribe({
      next: (data) => {
        this.profile = data || null;
        this.patientAddress = (data?.patient?.adresse || localStorage.getItem('optiClinicPatientAddress') || '').trim();
        this.isLoading = false;
        // Après chargement du profil, lancer récupération météo non bloquante
        if (!this.profile || !this.profile.appointments || this.profile.appointments.length === 0) {
          // fallback: récupérer rendez-vous confirmés du démon (dev)
          const url = `${this.apiUrl}/api/appointments`;
          this.http.get<any[]>(url).subscribe({
            next: (arr) => {
              // mapper la structure pour le front existant
              this.profile = this.profile || ({} as PatientProfile);
              this.profile.appointments = (arr || []).map((a, index) => ({
                id: Number(a.id || index + 1),
                dateRDV: a.date,
                heureDebut: a.time + ':00',
                heureFin: a.time + ':30',
                motifConsultation: `Rendez-vous confirmé avec ${a.doctor_name}`,
                statut: 'Confirmé',
                latitude: a.lat,
                longitude: a.lon
              }));
              this.populateWeatherForAppointments();
            },
            error: () => {
              // pas de fallback possible
              this.populateWeatherForAppointments();
            }
          });
        } else {
          this.populateWeatherForAppointments();
        }

        this.refreshTravelNotices();
      },
      error: (err) => {
        console.error('Erreur chargement profil patient:', err);
        // Prefer backend-provided message when available
        const backendMsg = err?.error?.message || err?.error?.error || err?.error?.access;
        if (err?.status === 401 || err?.status === 403) {
          this.errorMessage = backendMsg || 'Token manquant ou invalide. Veuillez vous connecter.';
        } else {
          this.errorMessage = backendMsg || 'Impossible de charger votre profil.';
        }
        this.isLoading = false;
      }
    });
  }

  goToLogin(): void {
    this.router.navigateByUrl('/login');
  }

  get isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  getAppointmentKey(item: any, index: number): string {
    return `${item.dateRDV || 'unknown'}-${item.heureDebut || '00:00'}-${index}`;
  }

  private populateWeatherForAppointments(): void {
    if (!this.profile || !this.profile.appointments) return;
    this.profile.appointments.forEach((item, idx) => this.fetchWeatherForAppointment(item, idx));
  }

  private startTravelRefreshLoop(): void {
    if (this.travelRefreshTimer) {
      return;
    }

    this.travelRefreshTimer = setInterval(() => {
      this.refreshTravelNotices();
    }, 15 * 60 * 1000);
  }

  private refreshTravelNotices(): void {
    const appointments = this.profile?.appointments || [];
    if (appointments.length === 0) {
      return;
    }

    this.http.get<TravelNoticesResponse>(this.apiUrl + '/patient/travel-notices').subscribe({
      next: (response) => {
        const nextMap: Record<number, TravelNoticeState> = {};

        (response?.notices || []).forEach((item) => {
          nextMap[item.rdvId] = {
            loading: false,
            notice: item.notice || null,
            error: item.notice?.status === 'error' ? item.notice.message || 'Notice indisponible' : null
          };

          this.maybeNotifyTravelNotice(item.rdvId, item.notice || null);
        });

        appointments.forEach((item) => {
          if (!item.id || nextMap[item.id]) {
            return;
          }

          nextMap[item.id] = {
            loading: false,
            notice: null,
            error: this.patientAddress ? 'Notice indisponible pour ce rendez-vous.' : 'Renseignez votre adresse pour calculer le trajet.'
          };
        });

        this.travelNoticeMap = nextMap;
      },
      error: () => {
        const message = this.patientAddress ? 'Impossible de calculer les notices de trajet.' : 'Renseignez votre adresse pour activer le calcul du trajet.';
        const fallbackMap: Record<number, TravelNoticeState> = {};
        appointments.forEach((item) => {
          if (item.id) {
            fallbackMap[item.id] = {
              loading: false,
              notice: null,
              error: message
            };
          }
        });
        this.travelNoticeMap = fallbackMap;
      }
    });
  }

  savePatientAddress(): void {
    const address = this.patientAddress.trim();
    if (!address) {
      this.addressMessage = 'Veuillez saisir votre adresse avant de l’enregistrer.';
      return;
    }

    this.addressSaving = true;
    this.addressMessage = '';

    this.http.put<{ message: string; adresse: string }>(this.apiUrl + '/patient/profile/address', { adresse: address }).subscribe({
      next: (response) => {
        this.addressSaving = false;
        this.patientAddress = (response?.adresse || address).trim();
        localStorage.setItem('optiClinicPatientAddress', this.patientAddress);
        this.addressMessage = 'Adresse enregistrée. Le calcul de trajet est mis à jour.';
        this.refreshTravelNotices();
      },
      error: () => {
        this.addressSaving = false;
        this.addressMessage = 'Impossible d’enregistrer votre adresse pour le moment.';
      }
    });
  }

  requestTravelNotificationsPermission(): void {
    if (typeof Notification === 'undefined') {
      this.addressMessage = 'Les notifications du navigateur ne sont pas disponibles.';
      return;
    }

    Notification.requestPermission().then((permission) => {
      this.travelNotificationsEnabled = permission === 'granted';
      this.addressMessage = this.travelNotificationsEnabled
        ? 'Notifications de trajet activées.'
        : 'Notifications de trajet désactivées.';
    });
  }

  getTravelNotice(item: { id?: number }): TravelNoticeState | null {
    if (!item.id) {
      return null;
    }

    return this.travelNoticeMap[item.id] || null;
  }

  getTrafficBadgeClass(level?: string | null): string {
    const normalized = (level || '').toLowerCase();
    if (normalized === 'dense') {
      return 'traffic-badge dense';
    }
    if (normalized === 'moyen') {
      return 'traffic-badge medium';
    }
    if (normalized === 'fluide') {
      return 'traffic-badge fluid';
    }
    return 'traffic-badge unknown';
  }

  private maybeNotifyTravelNotice(rdvId: number, notice: TravelNotice | null): void {
    if (!notice || !notice.should_notify || typeof Notification === 'undefined' || Notification.permission !== 'granted') {
      return;
    }

    const cacheKey = `${this.travelAlertPrefix}${rdvId}:${notice.checked_at || notice.departure_time || 'now'}`;
    if (localStorage.getItem(cacheKey)) {
      return;
    }

    localStorage.setItem(cacheKey, '1');
    new Notification(notice.notification_title || 'Trajet vers la clinique', {
      body: notice.notification_body || notice.recommendation || 'Notice de trajet disponible',
      icon: '/favicon.ico'
    });
  }

  isToday(dateStr?: string | null): boolean {
    if (!dateStr) return false;
    const today = new Date().toISOString().slice(0, 10);
    return dateStr === today;
  }

  fetchWeatherForAppointment(item: any, index: number): void {
    const key = this.getAppointmentKey(item, index);
    this.weatherMap[key] = { loading: true };

    const lat = (item.latitude || (item as any).cabinet?.latitude || 36.8).toString();
    const lon = (item.longitude || (item as any).cabinet?.longitude || 10.1).toString();

    const url = `${this.apiUrl}/weather`;

    this.http.get<any>(url, { params: { latitude: lat, longitude: lon } }).subscribe({
      next: (res) => {
        this.weatherMap[key] = {
          loading: false,
          temperature: res?.current_weather?.temperature ?? undefined,
          windspeed: res?.current_weather?.windspeed ?? undefined,
          recommendation: res?.weather_recommendation || res?.recommendation || null
        };
      },
      error: (err) => {
        console.warn('Météo non disponible pour', key, err);
        this.weatherMap[key] = { loading: false, recommendation: null };
      }
    });
  }

  formatShortDate(dateStr: string | null | undefined): string {
    if (!dateStr) {
      return '-';
    }
    try {
      const date = new Date(`${dateStr}T00:00:00`);
      if (Number.isNaN(date.getTime())) {
        return dateStr;
      }
      return date.toLocaleDateString('fr-FR', { year: 'numeric', month: '2-digit', day: '2-digit' });
    } catch {
      return dateStr;
    }
  }

  formatShortTime(timeStr: string | null | undefined): string {
    if (!timeStr) {
      return '-';
    }
    // timeStr is in HH:MM:SS format, return just HH:MM
    return timeStr.substring(0, 5) || timeStr;
  }

  getStatutBadgeClass(statut?: string | null): string {
    const lower = (statut || '').toLowerCase().trim();
    if (['termine', 'terminee', 'effectue', 'effectuee', 'realise', 'realisee'].includes(lower)) {
      return 'success-pill';
    }
    if (['annule', 'annulee', 'cancelled'].includes(lower)) {
      return 'danger-pill';
    }
    if (['reporte', 'reportee', 'postponed'].includes(lower)) {
      return 'warning-pill';
    }
    return 'info-pill';
  }

  canTrackCabinet(statut: string | null | undefined): boolean {
    const lower = (statut || '').toLowerCase();
    return lower.includes('programme') || lower.includes('confirm');
  }

  startCabinetTracking(rdv: any): void {
    this.selectedRdvForTracking = rdv;
    this.isTrackingModalOpen = true;
    this.isTracking = true;
    
    // Listen to cabinet status updates via socket
    this.socketService.onCabinetStatusUpdate()
      .pipe(takeUntil(this.destroy$))
      .subscribe((status: CabinetStatus) => {
        this.cabinetStatus = status;
      });

    // Request initial cabinet status
    this.socketService.requestCabinetStatus();
  }

  closeCabinetTracking(): void {
    this.isTrackingModalOpen = false;
    this.isTracking = false;
    this.selectedRdvForTracking = null;
    this.cabinetStatus = null;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/home']);
  }

  goHome(): void {
    this.router.navigate(['/home']);
  }

  toggleRdvList(): void {
    this.isRdvListExpanded = !this.isRdvListExpanded;
  }
}


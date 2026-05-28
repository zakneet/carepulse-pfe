import { Component, OnDestroy, OnInit } from '@angular/core';
import { catchError, map, of } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { PatientDashboardMedicalRecord, PatientTodayAccessResponse, Rdv, RdvService, SuggestedSlot } from '../services/rdv.service';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-rdv-list',
  templateUrl: './rdv-list.component.html',
  styleUrls: ['./rdv-list.component.css']
})
export class RdvListComponent implements OnInit, OnDestroy {

  rdvs: Rdv[] = [];
  // weather state per appointment key
  weatherMap: Record<string, { loading: boolean; temperature?: number; windspeed?: number; recommendation?: string | null }> = {};
  selectedRdv: Rdv | null = null;
  editSuggestedSlots: SuggestedSlot[] = [];
  errorMessage = '';
  cabinetErrorMessage = '';
  activeCabinetRdvId: number | null = null;
  activeCabinetPersonnelId: number | null = null;
  hasTodayCabinetAccess = false;
  doctorStatus = '';
  appointmentTime = '';
  totalPatients = 0;
  patientsWaiting = 0;
  waitTime = 0;
  dossierMedical: PatientDashboardMedicalRecord | null = null;

  private cabinetTimerId: ReturnType<typeof setInterval> | null = null;

  constructor(private rdvService: RdvService, private authService: AuthService, private http: HttpClient) {}

  ngOnInit(): void {
    this.getRdvs();
    this.loadTodayCabinetAccess();
    this.loadDossierMedical();
    this.startCabinetRefresh();
  }

  ngOnDestroy(): void {
    this.stopCabinetRefresh();
  }

  getRdvs(): void {  //il faut mettre id du patient en param
    const rdvsSource = this.authService.isPatient()
      ? this.rdvService.getPatientRdvs()
      : this.rdvService.getRdvs();

    rdvsSource
      .subscribe({
        next: (data) => {
          this.errorMessage = '';
          this.rdvs = data;
        },
        error: () => {
          if (!this.authService.isPatient()) {
            this.fetchDemoAppointmentsIfEmpty();
            return;
          }

          this.rdvService.getPatientDashboard().pipe(
            map((response) => (response.appointments || []).map((appointment) => ({
              id: appointment.id,
              idRdv: appointment.id,
              idRDV: appointment.id,
              idPatient: this.authService.getCurrentUser()?.id,
              dateRDV: appointment.dateRDV,
              heureDebut: appointment.heureDebut,
              heureFin: appointment.heureFin,
              motifConsultation: appointment.motifConsultation || '',
              statut: appointment.statut || '',
              personnelNom: appointment.medecinNom,
              personnelPrenom: appointment.medecinPrenom
            } as Rdv))),
            catchError(() => of<Rdv[]>([]))
          ).subscribe({
            next: (data) => {
              if (data.length > 0) {
                this.errorMessage = '';
                this.rdvs = data;
                this.populateWeatherForRdvs();
                return;
              }

              // si toujours rien, tenter le démon local (dev)
              this.fetchDemoAppointmentsIfEmpty();
            },
            error: () => {
              this.fetchDemoAppointmentsIfEmpty();
            }
          });
        }
      });

    // si la première source renvoie une liste vide, tenter le démon local
    rdvsSource.subscribe({
      next: (data) => {
        if (!data || data.length === 0) {
          this.fetchDemoAppointmentsIfEmpty();
        } else {
          this.populateWeatherForRdvs();
        }
      },
      error: () => {
        // ignore, handled above
      }
    });
  }

  private fetchDemoAppointmentsIfEmpty(): void {
    if (this.rdvs && this.rdvs.length > 0) return;
    const url = (environment as any).weatherUrl ? `${(environment as any).weatherUrl}/api/appointments` : '/api/appointments';
    this.http.get<any[]>(url).subscribe({
      next: (arr) => {
        if (!arr || arr.length === 0) return;
        this.rdvs = (arr || []).map(a => ({
          id: a.id,
          idRdv: a.id,
          idRDV: a.id,
          idPatient: this.authService.getCurrentUser()?.id,
          dateRDV: a.date,
          heureDebut: a.time + ':00',
          heureFin: a.time + ':30',
          motifConsultation: `Rendez-vous confirmé avec ${a.doctor_name}`,
          statut: 'Confirmé',
          personnelNom: a.doctor_name,
          latitude: a.lat,
          longitude: a.lon
        } as Rdv));
        this.populateWeatherForRdvs();
      },
      error: () => {
        // ignore
      }
    });
  }

  getRdvId(rdv: Rdv): number {
    const id = Number((rdv as unknown as Record<string, unknown>)['id']
      ?? (rdv as unknown as Record<string, unknown>)['idRdv']
      ?? (rdv as unknown as Record<string, unknown>)['idRDV']);
    return Number.isFinite(id) ? id : 0;
  }

  deleteRdv(id: number): void {
    const confirmed = window.confirm('Voulez-vous vraiment annuler ce rendez-vous ?');
    if (!confirmed) {
      return;
    }

    this.rdvService.deleteRdv(id)
      .subscribe({
        next: () => {
          this.errorMessage = '';
        this.getRdvs();
        },
        error: () => {
          this.errorMessage = 'La suppression a echoue. Verifiez la connexion au backend.';
        }
      });
  }

  editRdv(rdv: Rdv): void {
    this.selectedRdv = { ...rdv, id: this.getRdvId(rdv) };
    this.editSuggestedSlots = [];

    // Fetch suggested slots for this appointment to restrict edits
    const idPersonnel = (rdv as any).idPersonnel ? Number((rdv as any).idPersonnel) : undefined;
    if (!idPersonnel) return;

    const heureDebut = rdv.heureDebut || '';
    const heureFin = rdv.heureFin || '';
    const slotDuration = this.calculateMinutesBetween(heureDebut, heureFin) || 30;

    this.rdvService.suggestAvailableSlots({ idPersonnel, dateRDV: this.toDateOnly(rdv.dateRDV), isUrgent: false, slotDuration }).subscribe({
      next: (res) => {
        this.editSuggestedSlots = (res.optimizedSuggestedSlots && res.optimizedSuggestedSlots.length > 0) ? res.optimizedSuggestedSlots : (res.suggestedSlots || []);
        if (this.editSuggestedSlots.length > 0 && this.selectedRdv) {
          // default to first suggested slot
          this.selectedRdv.heureDebut = this.editSuggestedSlots[0].heureDebut;
          this.selectedRdv.heureFin = this.editSuggestedSlots[0].heureFin;
        }
      },
      error: () => {
        this.editSuggestedSlots = [];
      }
    });
  }

  updateRdv(): void {
    if (!this.selectedRdv) {
      return;
    }

    this.rdvService.updateRdv(this.selectedRdv).subscribe({
      next: () => {
        this.errorMessage = '';
        alert('RDV modifie');
        this.selectedRdv = null;
        this.getRdvs();
      },
      error: () => {
        this.errorMessage = 'La mise a jour a echoue. Verifiez la connexion au backend.';
      }
    });
  }

  onEditSlotChange(): void {
    if (!this.selectedRdv || !this.editSuggestedSlots) return;
    const found = this.editSuggestedSlots.find(s => s.heureDebut === this.selectedRdv!.heureDebut);
    if (found) {
      this.selectedRdv.heureFin = found.heureFin;
    }
  }

  private calculateMinutesBetween(start: string, end: string): number | null {
    if (!start || !end) return null;
    try {
      const [hs, ms] = start.split(':').map(Number);
      const [he, me] = end.split(':').map(Number);
      if (Number.isNaN(hs) || Number.isNaN(ms) || Number.isNaN(he) || Number.isNaN(me)) return null;
      return (he * 60 + me) - (hs * 60 + ms);
    } catch (e) {
      return null;
    }
  }

  cancelEdit(): void {
    this.selectedRdv = null;
    this.editSuggestedSlots = [];
  }

  toggleCabinetPanel(rdv: Rdv): void {
    // Allow opening the cabinet panel UI even if client-side access flag is false.
    const rdvId = this.getRdvId(rdv);
    if (!rdvId) {
      return;
    }

    // Refresh access state before toggling so the panel shows up-to-date info.
    this.activeCabinetRdvId = this.activeCabinetRdvId === rdvId ? null : rdvId;
    this.activeCabinetPersonnelId = (rdv as any).idPersonnel ? Number((rdv as any).idPersonnel) : null;
    this.loadTodayCabinetAccess();
  }

  isCabinetPanelOpenFor(rdv: Rdv): boolean {
    return this.activeCabinetRdvId === this.getRdvId(rdv);
  }

  canShowCabinetButton(rdv: Rdv): boolean {
    // Show the Cabinet button for appointments scheduled today.
    if (this.toDateOnly(rdv.dateRDV) !== this.getTodayIsoDate()) {
      return false;
    }

    const accessTime = this.normalizeTime(this.appointmentTime);
    if (!accessTime || accessTime === '--:--') {
      return true;
    }

    return this.normalizeTime(rdv.heureDebut) === accessTime;
  }

  private startCabinetRefresh(): void {
    this.stopCabinetRefresh();
    this.cabinetTimerId = setInterval(() => {
      this.loadTodayCabinetAccess();
    }, 30000);
  }

  private stopCabinetRefresh(): void {
    if (this.cabinetTimerId) {
      clearInterval(this.cabinetTimerId);
      this.cabinetTimerId = null;
    }
  }

  private loadTodayCabinetAccess(): void {
    // If there's no auth token and we have no local RDVs yet, show client fallback instead
    const token = this.authService.getToken();
    if (!token && (!this.rdvs || this.rdvs.length === 0)) {
      this.computeFallbackCabinetStats();
      return;
    }

    // If there's no token, use the first RDV's patient id as a fallback to avoid 401
    const fallbackPatientId = !token && this.rdvs && this.rdvs.length > 0 ? (this.rdvs[0].idPatient as number) : undefined;

    this.rdvService.getPatientTodayAccess(fallbackPatientId).subscribe({
      next: (response: PatientTodayAccessResponse) => {
        this.cabinetErrorMessage = '';
        this.applyCabinetAccess(response);
      },
      error: (errorResponse) => {
        // Backend unavailable or access denied: compute a client-side fallback
        this.hasTodayCabinetAccess = false;
        // Keep the panel open (do not nullify activeCabinetRdvId) so fallback can be shown
        this.cabinetErrorMessage = errorResponse?.error?.message || 'Suivi cabinet indisponible pour le moment.';
        this.computeFallbackCabinetStats();
      }
    });
  }

  private computeFallbackCabinetStats(): void {
    const today = this.getTodayIsoDate();
    const now = new Date();
    const nowMinutes = now.getHours() * 60 + now.getMinutes();

    // Filter by personnel if available so we show patients for the same doctor
    const todayRdvsAll = (this.rdvs || []).filter(r => this.toDateOnly(r.dateRDV) === today);
    const todayRdvs = this.activeCabinetPersonnelId
      ? todayRdvsAll.filter(r => Number((r as any).idPersonnel) === this.activeCabinetPersonnelId)
      : todayRdvsAll;
    const total = todayRdvs.length;
    let waiting = 0;
    let nearestWait: number | null = null;

    todayRdvs.forEach((r) => {
      const timeRaw = (r.heureDebut || '').slice(0, 5);
      if (!timeRaw) return;
      const parts = timeRaw.split(':');
      if (parts.length < 2) return;
      const mins = Number(parts[0]) * 60 + Number(parts[1]);
      if (mins > nowMinutes) {
        waiting += 1;
        const delta = mins - nowMinutes;
        if (nearestWait === null || delta < nearestWait) nearestWait = delta;
      }
    });

    this.totalPatients = Number(total || 0);
    this.patientsWaiting = Number(waiting || 0);
    this.waitTime = Number(nearestWait !== null ? nearestWait : 0);
    this.doctorStatus = 'indisponible';
    this.appointmentTime = '--:--';
    this.cabinetErrorMessage = '';
  }

  formatWaitTime(minutes: number | null | undefined): string {
    const totalMinutes = Number(minutes || 0);
    if (!Number.isFinite(totalMinutes) || totalMinutes <= 0) {
      return '0 min';
    }

    const hours = Math.floor(totalMinutes / 60);
    const remainingMinutes = totalMinutes % 60;

    if (hours <= 0) {
      return `${remainingMinutes} min`;
    }

    if (remainingMinutes <= 0) {
      return `${hours} h`;
    }

    return `${hours} h ${String(remainingMinutes).padStart(2, '0')} min`;
  }

  private loadDossierMedical(): void {
    this.rdvService.getPatientDashboard().subscribe({
      next: (response) => {
        this.dossierMedical = response.dossierMedical;
      },
      error: () => {
        this.dossierMedical = null;
      }
    });
  }

  private applyCabinetAccess(response: PatientTodayAccessResponse): void {
    this.hasTodayCabinetAccess = Boolean(response.access);
    if (!this.hasTodayCabinetAccess) {
      this.doctorStatus = response.doctor_status || '';
      this.appointmentTime = response.your_appointment_time || '';
      this.cabinetErrorMessage = response.message || 'Accès non autorisé pour le suivi aujourd\u2019hui.';
      // keep activeCabinetRdvId so the panel can show fallback info
      return;
    }

    this.doctorStatus = response.doctor_status || 'inconnu';
    this.appointmentTime = response.your_appointment_time || '--:--';
    this.totalPatients = Number(response.totalPatients || 0);
    this.patientsWaiting = Number(response.patientsWaiting || 0);
    this.waitTime = Number(response.waitTime || 0);
  }

  getTodayIsoDate(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  toDateOnly(value: string): string {
    return (value || '').slice(0, 10);
  }

  getAppointmentKey(item: any, index: number): string {
    return `${item.dateRDV || 'unknown'}-${item.heureDebut || '00:00'}-${index}`;
  }

  private populateWeatherForRdvs(): void {
    if (!this.rdvs) return;
    this.rdvs.forEach((item, idx) => this.fetchWeatherForAppointment(item, idx));
  }

  private fetchWeatherForAppointment(item: any, index: number): void {
    const key = this.getAppointmentKey(item, index);
    this.weatherMap[key] = { loading: true };

    const lat = (item.latitude || (item as any).cabinet?.latitude || 36.8).toString();
    const lon = (item.longitude || (item as any).cabinet?.longitude || 10.1).toString();
    const url = (environment as any).weatherUrl ? `${(environment as any).weatherUrl}/weather` : `${'/weather'}`;

    this.http.get<any>(url, { params: { latitude: lat, longitude: lon } }).subscribe({
      next: (res) => {
        this.weatherMap[key] = {
          loading: false,
          temperature: res?.current_weather?.temperature ?? undefined,
          windspeed: res?.current_weather?.windspeed ?? undefined,
          recommendation: res?.weather_recommendation || res?.recommendation || null
        };
      },
      error: () => {
        this.weatherMap[key] = { loading: false, recommendation: null };
      }
    });
  }

  getStatutBadgeClass(statut?: string | null): string {
    const lower = (statut || '').toLowerCase().trim();
    if (['termine', 'terminee', 'effectue', 'effectuee', 'realise', 'realisee'].includes(lower)) {
      return 'success-pill';
    }
    if (['annule', 'annulee', 'cancelled'].includes(lower) || lower.startsWith('annule')) {
      return 'cancelled-pill';
    }
    if (['reporte', 'reportee', 'postponed'].includes(lower)) {
      return 'warning-pill';
    }
    return 'info-pill';
  }

  isCancelledStatus(statut?: string | null): boolean {
    const lower = (statut || '').toLowerCase().trim();
    return ['annule', 'annulee', 'cancelled', 'annule (urgence medecin)'].includes(lower) || lower.startsWith('annule');
  }

  private normalizeTime(value: string): string {
    return (value || '').trim().slice(0, 5);
  }

}
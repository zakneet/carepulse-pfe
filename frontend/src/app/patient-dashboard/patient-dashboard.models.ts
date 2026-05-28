import { MedicalStaff, PatientDashboardAppointment, PatientDashboardMedicalRecord, PatientDashboardResponse, PatientTodayAccessResponse, SlotSuggestionResponse } from '../services/rdv.service';

export type AppointmentStatusTone = 'scheduled' | 'done' | 'cancelled' | 'delayed' | 'locked';

export interface DoctorProfileView extends MedicalStaff {
  region?: string | null;
  avatarLabel: string;
}

export interface PatientDashboardViewModel extends PatientDashboardResponse {
  patient: PatientDashboardResponse['patient'] & {
    initials?: string;
  };
}

export interface SingleSlotProposal extends SlotSuggestionResponse {
  recommendedSlot: { heureDebut: string; heureFin: string } | null;
}

export interface TravelNoticeView {
  rdvId: number;
  appointmentDate?: string | null;
  appointmentTime?: string | null;
  notice: {
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
}

export interface TravelNoticesResponse {
  patientId: number;
  patientAddress: string;
  clinicAddress: string;
  notices: TravelNoticeView[];
}

export interface WeatherWidgetView {
  loading: boolean;
  temperature?: number;
  windspeed?: number;
  recommendation?: string | null;
  status?: string;
}

export interface HistoryFilterOption {
  value: 'all' | 'scheduled' | 'done' | 'cancelled' | 'delayed';
  label: string;
}

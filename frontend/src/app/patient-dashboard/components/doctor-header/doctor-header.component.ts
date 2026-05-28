import { Component, Input } from '@angular/core';
import { MedicalStaff, PatientDashboardAppointment } from '../../../services/rdv.service';

@Component({
  selector: 'app-doctor-header',
  templateUrl: './doctor-header.component.html',
  styleUrls: ['./doctor-header.component.scss']
})
export class DoctorHeaderComponent {
  @Input() doctor: MedicalStaff | null = null;
  @Input() patientName = 'Patient';
  @Input() nextAppointment: PatientDashboardAppointment | null = null;
  @Input() hasSecureLink = false;

  get doctorLabel(): string {
    if (!this.doctor) {
      return 'Aucun médecin lié';
    }

    const fullName = `${(this.doctor.prenom || '').trim()} ${(this.doctor.nom || '').trim()}`.trim();
    return fullName || 'Médecin';
  }

  get avatarLabel(): string {
    if (!this.doctor) {
      return 'P';
    }

    return `${(this.doctor.prenom || '').charAt(0)}${(this.doctor.nom || '').charAt(0)}`.trim().toUpperCase() || 'M';
  }

  get specialtyLabel(): string {
    return this.doctor?.specialite?.trim() || 'Cabinet médical';
  }
}

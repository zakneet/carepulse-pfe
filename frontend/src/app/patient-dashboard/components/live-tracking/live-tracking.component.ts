import { Component, Input } from '@angular/core';
import { PatientTodayAccessResponse } from '../../../services/rdv.service';

@Component({
  selector: 'app-live-tracking',
  templateUrl: './live-tracking.component.html',
  styleUrls: ['./live-tracking.component.scss']
})
export class LiveTrackingComponent {
  @Input() access: PatientTodayAccessResponse | null = null;
  @Input() loading = false;
  @Input() locked = false;
  @Input() lockedMessage = '';
  @Input() nextAppointmentLabel = '';
}

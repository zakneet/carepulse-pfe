import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SingleSlotProposal, TravelNoticeView, WeatherWidgetView } from '../../patient-dashboard.models';

@Component({
  selector: 'app-appointment-suggestion',
  templateUrl: './appointment-suggestion.component.html',
  styleUrls: ['./appointment-suggestion.component.scss']
})
export class AppointmentSuggestionComponent {
  @Input() suggestion: SingleSlotProposal | null = null;
  @Input() doctorLabel = '';
  @Input() selectedDateLabel = '';
  @Input() loading = false;
  @Input() locked = false;
  @Input() lockedMessage = '';
  @Input() proposalIndex = 0;
  @Input() travelNotice: TravelNoticeView | null = null;
  @Input() weather: WeatherWidgetView | null = null;

  @Output() confirm = new EventEmitter<void>();
  @Output() another = new EventEmitter<void>();
}

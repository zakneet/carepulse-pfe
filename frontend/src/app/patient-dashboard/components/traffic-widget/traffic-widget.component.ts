import { Component, Input } from '@angular/core';
import { TravelNoticeView } from '../../patient-dashboard.models';

@Component({
  selector: 'app-traffic-widget',
  templateUrl: './traffic-widget.component.html',
  styleUrls: ['./traffic-widget.component.scss']
})
export class TrafficWidgetComponent {
  @Input() notice: TravelNoticeView | null = null;
  @Input() title = 'Trajet & circulation';
}

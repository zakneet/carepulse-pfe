import { Component, Input } from '@angular/core';
import { WeatherWidgetView } from '../../patient-dashboard.models';

@Component({
  selector: 'app-weather-widget',
  templateUrl: './weather-widget.component.html',
  styleUrls: ['./weather-widget.component.scss']
})
export class WeatherWidgetComponent {
  @Input() weather: WeatherWidgetView | null = null;
  @Input() title = 'Météo du jour';
}

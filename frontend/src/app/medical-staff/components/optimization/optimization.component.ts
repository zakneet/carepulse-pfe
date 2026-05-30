import { Component } from '@angular/core';

@Component({
  selector: 'app-optimization',
  templateUrl: './optimization.component.html',
  styleUrls: ['./optimization.component.css']
})
export class OptimizationComponent {
  score = 86;
  metrics = [
    { label: 'Scheduling efficiency', value: 92, unit: '%', trend: '+4%', color: 'green' },
    { label: 'Slot utilization',      value: 88, unit: '%', trend: '+6%', color: 'green' },
    { label: 'Patient wait time',     value: 32, unit: 'min', trend: '-8 min', color: 'blue' },
    { label: 'Auto-replacements',     value: 4,  unit: 'today', trend: '+2', color: 'violet' },
  ];
  recommendations = [
    { icon: '🔄', title: 'Auto-fill 14:00 slot', desc: 'Sophie Laurent (92% match) fits the freed 14:00 slot today.', action: 'Apply now', type: 'fill' },
    { icon: '⚡', title: 'Rebalance Thursday', desc: '3 appointments can be shifted to reduce patient wait time by 15 min.', action: 'Rebalance', type: 'rebalance' },
    { icon: '📋', title: 'Waiting list review', desc: '5 high-priority patients have been waiting > 7 days.', action: 'Review list', type: 'list' },
  ];
}

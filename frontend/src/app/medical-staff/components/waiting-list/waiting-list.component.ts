import { Component } from '@angular/core';

interface WaitingMatch {
  name: string;
  initials: string;
  consultationType: string;
  waitDuration: string;
  matchPct: number;
  priority: 'High' | 'Moderate' | 'Low';
  freedSlot: string;
  avatarColor: string;
}

@Component({
  selector: 'app-waiting-list',
  templateUrl: './waiting-list.component.html',
  styleUrls: ['./waiting-list.component.css']
})
export class WaitingListComponent {
  freedSlots = 3;

  matches: WaitingMatch[] = [
    { name: 'Sophie Laurent', initials: 'SL', consultationType: 'Cardiology follow-up', waitDuration: '3 days', matchPct: 92, priority: 'High', freedSlot: 'Today 14:00', avatarColor: 'linear-gradient(135deg,#0284c7,#38bdf8)' },
    { name: 'Marc Dubois', initials: 'MD', consultationType: 'Coronary artery check', waitDuration: '1 week', matchPct: 87, priority: 'High', freedSlot: 'Today 15:30', avatarColor: 'linear-gradient(135deg,#dc2626,#f87171)' },
    { name: 'Anna Petit', initials: 'AP', consultationType: 'Annual check-up', waitDuration: '5 days', matchPct: 81, priority: 'Moderate', freedSlot: 'Tomorrow 09:00', avatarColor: 'linear-gradient(135deg,#059669,#34d399)' },
    { name: 'Camille Rousseau', initials: 'CR', consultationType: 'Arrhythmia follow-up', waitDuration: '2 weeks', matchPct: 74, priority: 'Moderate', freedSlot: 'Tomorrow 11:00', avatarColor: 'linear-gradient(135deg,#7c3aed,#a78bfa)' },
    { name: 'Pierre Vidal', initials: 'PV', consultationType: 'Post-stent monitoring', waitDuration: '4 days', matchPct: 69, priority: 'Low', freedSlot: 'Fri 10:30', avatarColor: 'linear-gradient(135deg,#d97706,#fbbf24)' },
    { name: 'Émilie Chevalier', initials: 'ÉC', consultationType: 'Palpitations', waitDuration: '6 days', matchPct: 65, priority: 'High', freedSlot: 'Fri 09:00', avatarColor: 'linear-gradient(135deg,#0891b2,#22d3ee)' },
  ];

  getPriorityClass(priority: string): string {
    switch (priority) {
      case 'High':     return 'wl-priority--high';
      case 'Moderate': return 'wl-priority--moderate';
      default:         return 'wl-priority--low';
    }
  }
}

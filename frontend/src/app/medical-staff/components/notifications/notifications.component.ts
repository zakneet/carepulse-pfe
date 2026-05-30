import { Component } from '@angular/core';
@Component({ selector:'app-notifications', templateUrl:'./notifications.component.html', styleUrls:['./notifications.component.css'] })
export class NotificationsComponent {
  notifications = [
    { type:'emergency', title:'Emergency: M. Dubois', body:'Acute chest pain — slot moved to 09:45 today.', time:'2 min ago', read:false },
    { type:'ai',        title:'AI Optimization complete', body:'Your schedule has been re-optimized. 4 slots filled automatically.', time:'15 min ago', read:false },
    { type:'match',     title:'Waiting list match', body:'2 patients fit the freed 14:00 slot today.', time:'32 min ago', read:false },
    { type:'info',      title:'Appointment confirmed', body:'Sophie Laurent confirmed her 14:00 appointment.', time:'1h ago', read:true },
    { type:'info',      title:'Patient arrived early', body:'Marc Dubois checked in 20 minutes early.', time:'2h ago', read:true },
    { type:'system',    title:'Weekly report ready', body:'Your performance report for W22 is available.', time:'Yesterday', read:true },
    { type:'system',    title:'System update', body:'OptiClinic v2.3.1 deployed. OR-Tools engine upgraded.', time:'2 days ago', read:true },
  ];
  getTypeClass(type:string){ switch(type){ case 'emergency': return 'notif--emergency'; case 'ai': return 'notif--ai'; case 'match': return 'notif--match'; default: return 'notif--info'; } }
  markAllRead(){ this.notifications.forEach(n=>n.read=true); }
}

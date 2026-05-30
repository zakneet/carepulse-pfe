import { Component } from '@angular/core';
@Component({ selector:'app-settings', templateUrl:'./settings.component.html', styleUrls:['./settings.component.css'] })
export class SettingsComponent {
  sections = [
    { icon:'👤', title:'Profile', desc:'Update your name, photo and specialty', badge:null },
    { icon:'🔔', title:'Notifications', desc:'Configure alert channels and priority filters', badge:'3 unread' },
    { icon:'🤖', title:'AI Engine', desc:'Adjust optimization weights and auto-fill rules', badge:'Active' },
    { icon:'🔒', title:'Security', desc:'Password, 2FA and active sessions', badge:null },
    { icon:'📅', title:'Schedule preferences', desc:'Working hours, break durations, slot sizes', badge:null },
    { icon:'🎨', title:'Appearance', desc:'Theme, density and language', badge:null },
  ];
  aiEnabled = true;
  autoFill = true;
  realTimeAlerts = true;
}

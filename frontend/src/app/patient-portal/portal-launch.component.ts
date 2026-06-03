import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-portal-launch',
  template: `
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f0f9ff;font-family:'Inter',system-ui,sans-serif;">
      <div style="text-align:center;">
        <div style="width:48px;height:48px;border:3px solid #e2e8f0;border-top-color:#0284c7;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 1rem;"></div>
        <p style="color:#475569;font-weight:600;">Chargement de votre espace patient…</p>
      </div>
    </div>
  `,
  styles: [`@keyframes spin { to { transform: rotate(360deg); } }`]
})
export class PortalLaunchComponent implements OnInit {
  constructor(private router: Router) {}

  ngOnInit(): void {
    const savedPath = localStorage.getItem('opticlinic_last_patient_portal_path');
    console.log('[pwa-patient] portal-launch activated');

    if (savedPath && savedPath.startsWith('/patient/portal/')) {
      console.log('[pwa-patient] saved portal path found, redirecting');
      this.router.navigateByUrl(savedPath);
    } else {
      console.log('[pwa-patient] no saved portal path, going to /home');
      this.router.navigateByUrl('/home');
    }
  }
}

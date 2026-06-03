import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter, Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements AfterViewInit, OnDestroy {
  title = 'test';
  showMedicalHeader = false;
  private routerSubscription?: Subscription;

  constructor(private router: Router) {}

  ngAfterViewInit(): void {
    this.updateHeaderVisibility(this.router.url);

    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event) => {
        const nav = event as NavigationEnd;
        this.updateHeaderVisibility(nav.urlAfterRedirects || nav.url);
      });

    // PWA Standalone Redirect logic
    setTimeout(() => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone;
      const currentPath = window.location.pathname;
      if (isStandalone && (currentPath === '/' || currentPath === '/index.html' || currentPath === '')) {
        const lastPortalPath = localStorage.getItem('opticlinic_last_patient_portal_path');
        if (lastPortalPath && lastPortalPath.startsWith('/patient/portal/')) {
          this.router.navigateByUrl(lastPortalPath);
        }
      }
    }, 100);
  }

  ngOnDestroy(): void {
    this.routerSubscription?.unsubscribe();
  }

  private updateHeaderVisibility(url: string): void {
    // Home has its own navbar — no global medical header on public pages.
    this.showMedicalHeader = false;
  }
}

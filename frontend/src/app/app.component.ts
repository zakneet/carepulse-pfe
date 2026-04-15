import { AfterViewInit, Component, HostListener, OnDestroy } from '@angular/core';
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
  private revealObserver?: IntersectionObserver;
  private routerSubscription?: Subscription;

  constructor(private router: Router) {}

  @HostListener('window:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    const x = event.clientX / window.innerWidth;
    const y = event.clientY / window.innerHeight;

    document.documentElement.style.setProperty('--px', x.toFixed(3));
    document.documentElement.style.setProperty('--py', y.toFixed(3));
  }

  ngAfterViewInit(): void {
    this.setupRevealObserver();
    this.observeRevealTargets();
    this.updateHeaderVisibility(this.router.url);

    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event) => {
        this.observeRevealTargets();
        const nav = event as NavigationEnd;
        this.updateHeaderVisibility(nav.urlAfterRedirects || nav.url);
      });
  }

  ngOnDestroy(): void {
    this.revealObserver?.disconnect();
    this.routerSubscription?.unsubscribe();
  }

  private setupRevealObserver(): void {
    if (!('IntersectionObserver' in window)) {
      return;
    }

    this.revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
  }

  private observeRevealTargets(): void {
    if (!this.revealObserver) {
      return;
    }

    document.querySelectorAll('.reveal').forEach(element => {
      this.revealObserver?.observe(element);
    });
  }

  private updateHeaderVisibility(url: string): void {
    const cleanUrl = (url || '').toLowerCase();
    this.showMedicalHeader = cleanUrl.startsWith('/medical-staff');
  }
}

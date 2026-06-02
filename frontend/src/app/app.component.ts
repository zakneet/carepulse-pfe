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
  }

  ngOnDestroy(): void {
    this.routerSubscription?.unsubscribe();
  }

  private updateHeaderVisibility(url: string): void {
    // Home has its own navbar — no global medical header on public pages.
    this.showMedicalHeader = false;
  }
}

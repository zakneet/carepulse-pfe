import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { UserRole } from 'src/app/models/auth.model';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-home',
  template: `
<main class="patient-public-shell home-dark-shell">
  <header class="topbar dark-topbar">
    <a class="brand" routerLink="/home" aria-label="opticlinic accueil">
      <span class="brand-mark">o</span>
      <span class="brand-text">
        <strong>opticlinic</strong>
      </span>
    </a>

    <nav class="topnav" aria-label="Navigation principale">
      <a href="#accueil">Accueil</a>
      <a href="#services">Services</a>
    </nav>

    <div *ngIf="isAuthenticated" class="user-menu" (click)="onMenuClick($event)">
      <button type="button" class="user-menu-trigger" (click)="toggleUserMenu($event)" aria-haspopup="true" [attr.aria-expanded]="isUserMenuOpen">
        {{ getCurrentUserLabel() }}
        <span class="caret" [class.open]="isUserMenuOpen">▾</span>
      </button>

      <div class="user-menu-panel" *ngIf="isUserMenuOpen">
        <button type="button" class="menu-item" (click)="goToAccount()">Mon compte</button>
        <button type="button" class="menu-item" (click)="goToHelp()">Centre d'aide</button>
        <button type="button" class="menu-item danger" (click)="logout()">Se deconnecter</button>
      </div>
    </div>
  </header>

  <section id="accueil" class="hero-section hero-dark">
    <div class="hero-grid">
      <div class="hero-slogan hero-copy-dark">
        <p class="eyebrow">OptiClinic · Accueil</p>
        <h1 class="slogan">Gestion simple et rapide<br>de vos rendez-vous médicaux</h1>
        <p class="hero-text">
          OptiClinic rend la prise de rendez-vous facile et intuitive, dans un univers sombre et cohérent avec le reste de l’application.
        </p>
        <div class="patient-actions">
          <a routerLink="/patient/booking" class="primary-action">Prendre un rendez-vous</a>
          <a routerLink="/patient/rdvs" class="secondary-action">Mes rendez-vous</a>
        </div>
      </div>

      <div class="hero-visual-side hero-visual-dark">
        <div class="hero-panel">
          <div class="panel-top">
            <span class="pill">Dashboard</span>
            <span class="panel-status">Météo intégrée</span>
          </div>
          <div class="panel-card panel-card-large">
            <strong>Nadine Dhaou</strong>
            <p>Rendez-vous du jour</p>
          </div>
          <div class="panel-card panel-card-small">
            <span>☀️</span>
            <div>
              <strong>24.3 °C</strong>
              <p>Météo favorable</p>
            </div>
          </div>
          <div class="panel-card panel-card-small accent">
            <span>📅</span>
            <div>
              <strong>3 rendez-vous</strong>
              <p>Confirmés</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="services" class="content-section content-dark">
    <div class="section-heading dark-heading">
      <h2>Pourquoi choisir OptiClinic ?</h2>
      <p>Une interface cohérente, lisible et pensée pour les patients.</p>
    </div>

    <div class="feature-grid dark-feature-grid">
      <article class="feature-card dark-feature-card">
        <div class="feature-icon">📅</div>
        <h3>Simple</h3>
        <p>Interface claire et facile à utiliser</p>
      </article>

      <article class="feature-card dark-feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Rapide</h3>
        <p>Réservez en quelques clics</p>
      </article>

      <article class="feature-card dark-feature-card">
        <div class="feature-icon">🔔</div>
        <h3>Fiable</h3>
        <p>Rappels automatiques pour ne rien oublier</p>
      </article>
    </div>
  </section>
</main>
`,
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {
  isUserMenuOpen = false;
  isAuthenticated = false;

  private readonly subscriptions = new Subscription();

  constructor(
    public authService: AuthService,
    private router: Router
  ) {
    this.subscriptions.add(
      this.authService.authState$.subscribe((state) => {
        this.isAuthenticated = state.isAuthenticated;
        if (!state.isAuthenticated) {
          this.isUserMenuOpen = false;
        }
      })
    );
  }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  @HostListener('document:click')
  onDocumentClick(): void {
    this.isUserMenuOpen = false;
  }

  toggleUserMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }

  onMenuClick(event: MouseEvent): void {
    event.stopPropagation();
  }

  getCurrentUserLabel(): string {
    const user = this.authService.getCurrentUser();
    if (!user) {
      return 'Mon compte';
    }

    const fullName = `${user.prenom || ''} ${user.nom || ''}`.trim();
    return fullName || 'Mon compte';
  }

  getAccountRoute(): string {
    const role = this.authService.getUserRole();
    if (role === UserRole.MEDICAL_STAFF) {
      return '/medical-staff/doctor/planning';
    }
    if (role === UserRole.PATIENT) {
      return '/patient/dashboard';
    }
    return '/profile';
  }

  goToAccount(): void {
    this.isUserMenuOpen = false;
    this.router.navigate([this.getAccountRoute()]);
  }

  goToHelp(): void {
    this.isUserMenuOpen = false;
    this.router.navigate(['/home'], { fragment: 'services' });
  }

  logout(): void {
    this.authService.logout();
    this.isUserMenuOpen = false;
    this.router.navigate(['/home']);
  }
}

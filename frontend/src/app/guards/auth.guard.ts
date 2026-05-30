import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    // Build the full URL including the route segment being activated
    const targetUrl = state.url || this.buildUrlFromRoute(route);

    // Allow the authenticate page itself to always pass
    if (targetUrl === '/medical-staff/authenticate' || targetUrl.startsWith('/medical-staff/authenticate?')) {
      return true;
    }

    // Protect every /medical-staff route
    if (targetUrl.startsWith('/medical-staff')) {
      if (this.authService.isAuthenticated() && this.authService.isMedicalStaff()) {
        return true;
      }

      // Not authenticated → redirect to access code page, save return URL
      const returnUrl = targetUrl !== '/medical-staff' ? targetUrl : '/medical-staff/doctor/dashboard';
      this.router.navigate(['/medical-staff/authenticate'], { queryParams: { returnUrl } });
      return false;
    }

    // All other routes are public
    return true;
  }

  /** Reconstruct URL from the activated route snapshot tree (used as fallback). */
  private buildUrlFromRoute(route: ActivatedRouteSnapshot): string {
    const segments: string[] = [];
    let current: ActivatedRouteSnapshot | null = route;
    while (current) {
      if (current.url && current.url.length) {
        segments.unshift(...current.url.map(s => s.path));
      }
      current = current.parent;
    }
    return '/' + segments.join('/');
  }
}

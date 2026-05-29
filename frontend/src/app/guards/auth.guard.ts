import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    if (state.url.startsWith('/medical-staff') && state.url !== '/medical-staff/authenticate') {
      if (this.authService.isAuthenticated() && this.authService.isMedicalStaff()) {
        return true;
      }
      
      // Store return url for redirect
      this.router.navigate(['/medical-staff/authenticate'], { queryParams: { returnUrl: state.url } });
      return false;
    }
    
    // Default allow for other routes (can be expanded later for patients)
    return true;
  }
}

import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
      return false;
    }

    // Récupérer les rôles requis depuis la configuration de la route
    const requiredRoles: UserRole[] = route.data['roles'];

    if (!requiredRoles || requiredRoles.length === 0) {
      return true; // Pas de restriction de rôle
    }

    const userRole = this.authService.getUserRole();
    if (userRole && requiredRoles.includes(userRole)) {
      return true;
    }

    // Accès refusé pour la route demandée: rediriger vers login pour éviter
    // de renvoyer l'utilisateur dans un autre espace par erreur.
    this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });

    return false;
  }
}

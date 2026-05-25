import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService, private router: Router) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Ajouter le token JWT si disponible
    const token = this.authService.getToken();
    // log minimal pour debug (token partiel)
    try {
      const tokenPreview = token ? `${token.substring(0, 10)}...` : 'null';
      // eslint-disable-next-line no-console
      console.debug(`[JwtInterceptor] ${request.method} ${request.url} token=${tokenPreview}`);
    } catch (e) {
      // ignore
    }
    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        const isTodayAccess403 =
          request.url.includes('/patient/today-access') && error.status === 403;

        // log erreur HTTP pour debug
        try {
          const tokenPreview = token ? `${token.substring(0, 10)}...` : 'null';
          // eslint-disable-next-line no-console
          console.warn(`[JwtInterceptor] HTTP ${error.status} for ${request.method} ${request.url} token=${tokenPreview}`);
        } catch (e) {}

        if (isTodayAccess403) {
          return throwError(() => error);
        }

        // Si 401 ou 403, on nettoie l'etat local sans renvoyer vers une page de connexion supprimée.
        if (error.status === 401 || error.status === 403) {
          this.authService.logout();
        }
        return throwError(() => error);
      })
    );
  }
}

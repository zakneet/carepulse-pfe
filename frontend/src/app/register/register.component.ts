import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from 'src/environments/environment';

@Component({
	selector: 'app-register',
	templateUrl: './register.component.html',
	styleUrls: ['./register.component.css']
})
export class RegisterComponent {
	user: any = {
		nom: '',
		prenom: '',
		telephone: '',
		email: '',
		password: '',
		statut: 1
	};

	message = '';
	showPassword = false;
	showConfirmPassword = false;
	confirmPassword = '';
	returnUrl = '';

	constructor(private http: HttpClient, private router: Router, private route: ActivatedRoute) {
		this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';
	}

	register(): void {
		this.message = '';

		if (this.user.password !== this.confirmPassword) {
			this.message = 'Les mots de passe ne correspondent pas.';
			return;
		}

		this.http.post(`${environment.apiUrl}/register`, this.user)
			.subscribe({
				next: () => {
					this.router.navigate([this.returnUrl || '/home']);
				},
				error: (errorResponse) => {
					this.message = errorResponse?.error?.error || 'Creation du compte impossible.';
				}
			});
	}

	togglePassword(): void {
		this.showPassword = !this.showPassword;
	}

	toggleConfirmPassword(): void {
		this.showConfirmPassword = !this.showConfirmPassword;
	}
}

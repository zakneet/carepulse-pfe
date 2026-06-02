import { Component, ElementRef, OnInit, QueryList, ViewChildren } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UserType } from '../../models/auth.model';

@Component({
  selector: 'app-authenticate',
  templateUrl: './authenticate.component.html',
  styleUrls: ['./authenticate.component.css']
})
export class AuthenticateComponent implements OnInit {
  readonly codeLength = 6;
  digits: string[] = Array(this.codeLength).fill('');
  showCode = false;
  step: 'form' | 'loading' | 'success' | 'denied' = 'form';
  errorMessage = '';
  returnUrl = '';

  @ViewChildren('codeInput') codeInputs!: QueryList<ElementRef<HTMLInputElement>>;

  get isLoading(): boolean { return this.step === 'loading'; }
  get isSuccess(): boolean { return this.step === 'success'; }
  get isDenied(): boolean { return this.step === 'denied'; }

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '';
  }

  get accessCode(): string {
    return this.digits.join('').trim();
  }

  onDigitInput(index: number, event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = (input.value || '').replace(/\s/g, '').slice(-1).toUpperCase();
    this.digits[index] = value;
    input.value = value;

    if (value && index < this.codeLength - 1) {
      this.focusInput(index + 1);
    }

    if (this.accessCode.length === this.codeLength) {
      setTimeout(() => this.authenticate(), 120);
    }
  }

  onDigitKeydown(index: number, event: KeyboardEvent): void {
    if (event.key === 'Backspace' && !this.digits[index] && index > 0) {
      this.focusInput(index - 1);
    }
  }

  onPaste(event: ClipboardEvent): void {
    event.preventDefault();
    const pasted = (event.clipboardData?.getData('text') || '').replace(/\s/g, '').toUpperCase().slice(0, this.codeLength);
    if (!pasted) return;

    pasted.split('').forEach((char, i) => {
      this.digits[i] = char;
    });

    const inputs = this.codeInputs?.toArray() || [];
    inputs.forEach((ref, i) => {
      if (ref?.nativeElement) {
        ref.nativeElement.value = this.digits[i] || '';
      }
    });

    if (pasted.length === this.codeLength) {
      setTimeout(() => this.authenticate(), 120);
    } else {
      this.focusInput(Math.min(pasted.length, this.codeLength - 1));
    }
  }

  toggleShowCode(): void {
    this.showCode = !this.showCode;
  }

  authenticate(): void {
    this.errorMessage = '';
    this.step = 'form';

    if (this.accessCode.length !== this.codeLength) {
      this.errorMessage = `Le code doit contenir ${this.codeLength} caracteres.`;
      this.triggerDenied();
      return;
    }

    this.step = 'loading';

    this.authService.login({
      userType: UserType.MEDICAL_STAFF,
      accessCode: this.accessCode
    }).subscribe({
      next: () => {
        this.step = 'success';
        setTimeout(() => this.navigateToDashboard(), 1400);
      },
      error: (error) => {
        this.step = 'form';
        this.triggerDenied();
        if (error.status === 0) {
          this.errorMessage = 'Serveur inaccessible. Verifiez votre connexion.';
        } else if (error.status === 401 || error.status === 400 || error.status === 404) {
          this.errorMessage = 'Code d\'acces invalide.';
        } else if (error.error?.message) {
          this.errorMessage = error.error.message;
        } else {
          this.errorMessage = 'Acces refuse.';
        }
        this.digits = Array(this.codeLength).fill('');
        setTimeout(() => this.focusInput(0), 300);
      }
    });
  }

  private triggerDenied(): void {
    this.step = 'denied';
    setTimeout(() => {
      if (this.step === 'denied') {
        this.step = 'form';
      }
    }, 600);
  }

  private focusInput(index: number): void {
    const inputs = this.codeInputs?.toArray() || [];
    const target = inputs[index]?.nativeElement;
    if (target) {
      target.focus();
      target.select();
    }
  }

  private navigateToDashboard(): void {
    if (this.returnUrl && this.returnUrl !== '/medical-staff' && !this.returnUrl.endsWith('/medical-staff')) {
      this.router.navigateByUrl(this.returnUrl);
      return;
    }

    if (this.authService.isNurse()) {
      this.router.navigate(['/medical-staff/nurse/dashboard']);
    } else {
      this.router.navigate(['/medical-staff/doctor/dashboard']);
    }
  }
}

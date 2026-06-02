import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-logo',
  templateUrl: './logo.component.html',
  styleUrls: ['./logo.component.css']
})
export class LogoComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() showText = false;
  @Input() variant: 'default' | 'light' = 'default';

  get sizeClass(): string {
    return `logo--${this.size}`;
  }
}

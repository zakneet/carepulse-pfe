import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  doctors: any[] = [];
  isLoading: boolean = true;

  // Fallback data if API fails or returns empty
  private fallbackDoctors = [
    { nom: 'Ben Salah', prenom: 'Amira', specialite: 'Médecine générale' },
    { nom: 'Trabelsi', prenom: 'Karim', specialite: 'Cardiologie' },
    { nom: 'Mansour', prenom: 'Leïla', specialite: 'Dermatologie' },
    { nom: 'Haddad', prenom: 'Youssef', specialite: 'Pédiatrie' },
    { nom: 'Gharbi', prenom: 'Sami', specialite: 'Dentaire' },
    { nom: 'Cherif', prenom: 'Nadia', specialite: 'Ophtalmologie' }
  ];

  constructor(private router: Router, private http: HttpClient) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.http.get<any>('http://localhost:5000/medical-staff').subscribe({
      next: (res) => {
        const dataArray = Array.isArray(res) ? res : (res.data || []);
        if (dataArray && dataArray.length > 0) {
          this.doctors = dataArray.slice(0, 6);
        } else {
          this.doctors = [...this.fallbackDoctors];
        }
        this.isLoading = false;
      },
      error: () => { 
        console.error('API failed, using fallback mock data for doctors.');
        this.doctors = [...this.fallbackDoctors]; 
        this.isLoading = false;
      }
    });
  }

  onSearch(spec: string, region: string): void {
    const queryParams: any = {};
    if (spec?.trim()) queryParams.specialite = spec.trim();
    if (region?.trim()) queryParams.region = region.trim();
    
    this.router.navigate(['/doctors'], { queryParams });
  }

  bookDoctor(doc: any): void {
    const q: any = {};
    if (doc.specialite) q.specialite = doc.specialite;
    if (doc.id_personnel) q.idPersonnel = doc.id_personnel;
    else if (doc.id) q.idPersonnel = doc.id;
    this.router.navigate(['/patient/booking'], { queryParams: q });
  }

  getInitials(name: string): string {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map(w => w[0]).join('').toUpperCase().slice(0, 2);
  }

  getAvatarColor(name: string): string {
    const colors = ['bg-[#0ea5e9]', 'bg-[#ef4444]', 'bg-[#a855f7]', 'bg-[#10b981]', 'bg-[#f59e0b]', 'bg-[#3b82f6]'];
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
  }

  getReviews(name: string): { rating: number, count: number, exp: number } {
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return {
      rating: 4.5 + (Math.abs(hash) % 6) / 10,
      count: 100 + (Math.abs(hash) % 400),
      exp: 8 + (Math.abs(hash) % 15)
    };
  }

  scrollTo(id: string, e: Event): void {
    e.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  }
}
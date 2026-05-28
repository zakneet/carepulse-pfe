import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-doctors',
  templateUrl: './doctors.component.html',
  styleUrls: ['./doctors.component.css']
})
export class DoctorsComponent implements OnInit {
  doctors: any[] = [];
  isLoading = false;
  
  region: string = '';
  specialite: string = '';

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.region = params['region'] || '';
      this.specialite = params['specialite'] || '';
      this.fetchDoctors();
    });
  }

  fetchDoctors(): void {
    this.isLoading = true;
    let url = 'http://localhost:5000/medical-staff?';
    if (this.specialite) url += `specialite=${encodeURIComponent(this.specialite)}&`;
    if (this.region) url += `region=${encodeURIComponent(this.region)}&`;
    
    this.http.get<any>(url).subscribe({
      next: (res) => {
        const dataArray = Array.isArray(res) ? res : (res.data || []);
        this.doctors = dataArray;
        this.isLoading = false;
      },
      error: () => { 
        console.error('Failed to fetch doctors.');
        this.doctors = [];
        this.isLoading = false;
      }
    });
  }

  bookDoctor(doc: any): void {
    const id = doc.id_personnel || doc.id;
    if (id) {
      this.router.navigate(['/booking', id]);
    }
  }

  getInitials(name: string): string {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map(w => w[0]).join('').toUpperCase().slice(0, 2);
  }

  getAvatarColor(name: string): string {
    const gradients = [
      'from-blue-400 to-cyan-300',
      'from-purple-500 to-pink-400',
      'from-emerald-400 to-teal-300',
      'from-orange-400 to-amber-300',
      'from-indigo-500 to-blue-400',
      'from-rose-400 to-red-400'
    ];
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return gradients[Math.abs(hash) % gradients.length];
  }

  getReviews(name: string): { rating: number, count: number, exp: number } {
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return {
      rating: 4.5 + (Math.abs(hash) % 6) / 10,
      count: 50 + (Math.abs(hash) % 300),
      exp: 5 + (Math.abs(hash) % 20)
    };
  }
}

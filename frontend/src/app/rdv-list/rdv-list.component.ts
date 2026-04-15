import { Component, OnDestroy, OnInit } from '@angular/core';
import { Rdv, RdvService } from '../services/rdv.service';

@Component({
  selector: 'app-rdv-list',
  templateUrl: './rdv-list.component.html',
  styleUrls: ['./rdv-list.component.css']
})
export class RdvListComponent implements OnInit, OnDestroy {

  rdvs: Rdv[] = [];
  selectedRdv: Rdv | null = null;
  errorMessage = '';

  constructor(private rdvService: RdvService) {}

  ngOnInit(): void {
    this.getRdvs();
  }

  ngOnDestroy(): void {}

  getRdvs(): void {  //il faut mettre id du patient en param
    this.rdvService.getRdvs()
      .subscribe({
        next: (data) => {
          this.errorMessage = '';
        this.rdvs = data;
        },
        error: () => {
          this.errorMessage = 'Impossible de charger les rendez-vous depuis le backend.';
        }
      });
  }

  getRdvId(rdv: Rdv): number {
    const id = Number((rdv as unknown as Record<string, unknown>)['id']
      ?? (rdv as unknown as Record<string, unknown>)['idRdv']
      ?? (rdv as unknown as Record<string, unknown>)['idRDV']);
    return Number.isFinite(id) ? id : 0;
  }

  deleteRdv(id: number): void {
    const confirmed = window.confirm('Voulez-vous vraiment supprimer ce rendez-vous ?');
    if (!confirmed) {
      return;
    }

    this.rdvService.deleteRdv(id)
      .subscribe({
        next: () => {
          this.errorMessage = '';
        this.getRdvs();
        },
        error: () => {
          this.errorMessage = 'La suppression a echoue. Verifiez la connexion au backend.';
        }
      });
  }

  editRdv(rdv: Rdv): void {
    this.selectedRdv = { ...rdv, id: this.getRdvId(rdv) };
  }

  updateRdv(): void {
    if (!this.selectedRdv) {
      return;
    }

    this.rdvService.updateRdv(this.selectedRdv).subscribe({
      next: () => {
        this.errorMessage = '';
        alert('RDV modifie');
        this.selectedRdv = null;
        this.getRdvs();
      },
      error: () => {
        this.errorMessage = 'La mise a jour a echoue. Verifiez la connexion au backend.';
      }
    });
  }

  cancelEdit(): void {
    this.selectedRdv = null;
  }

}
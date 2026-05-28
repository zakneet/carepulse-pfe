import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { SingleSlotProposal } from '../patient-dashboard.models';

@Injectable({ providedIn: 'root' })
export class PlanningService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  suggestSingleSlot(idPersonnel: number, dateRDV: string, slotDuration = 30, proposalIndex = 0): Observable<SingleSlotProposal> {
    return this.http.post<SingleSlotProposal>(`${this.apiUrl}/suggest-available-slots`, {
      idPersonnel,
      dateRDV,
      slotDuration,
      proposalIndex,
      isUrgent: false,
    }).pipe(
      map((response) => ({
        ...response,
        recommendedSlot: response.optimizedSuggestedSlots?.[0] || response.suggestedSlots?.[0] || null,
      }))
    );
  }
}

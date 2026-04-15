import { Injectable } from '@angular/core';

/**
 * Guarantees that at most ONE RdvListComponent instance can be visible at a time.
 * This is a defensive guard against accidental double rendering.
 */
@Injectable({
  providedIn: 'root'
})
export class RdvListSingletonService {
  private ownerId: string | null = null;

  claim(id: string): boolean {
    if (this.ownerId === null) {
      this.ownerId = id;
      return true;
    }

    return this.ownerId === id;
  }

  release(id: string): void {
    if (this.ownerId === id) {
      this.ownerId = null;
    }
  }
}

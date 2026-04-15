import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DemandeRdvComponent } from './demande-rdv.component';

describe('DemandeRdvComponent', () => {
  let component: DemandeRdvComponent;
  let fixture: ComponentFixture<DemandeRdvComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DemandeRdvComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DemandeRdvComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

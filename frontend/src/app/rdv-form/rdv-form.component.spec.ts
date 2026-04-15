import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RdvFormComponent } from './rdv-form.component';

describe('RdvFormComponent', () => {
  let component: RdvFormComponent;
  let fixture: ComponentFixture<RdvFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RdvFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RdvFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

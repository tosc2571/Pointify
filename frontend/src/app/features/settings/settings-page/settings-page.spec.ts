import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { SettingsPage } from './settings-page';

describe('SettingsPage', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SettingsPage],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('loads and displays the current setting', () => {
    const fixture = TestBed.createComponent(SettingsPage);
    fixture.detectChanges();

    httpMock.expectOne('/api/settings').flush({ auto_backup_enabled: true });
    fixture.detectChanges();

    const checkbox: HTMLInputElement = fixture.nativeElement.querySelector('input[type="checkbox"]');
    expect(checkbox.checked).toBe(true);
  });

  it('toggles the setting via PUT and updates the view', () => {
    const fixture = TestBed.createComponent(SettingsPage);
    fixture.detectChanges();
    httpMock.expectOne('/api/settings').flush({ auto_backup_enabled: true });
    fixture.detectChanges();

    fixture.nativeElement.querySelector('input[type="checkbox"]').dispatchEvent(new Event('change'));

    const req = httpMock.expectOne('/api/settings');
    expect(req.request.method).toBe('PUT');
    expect(req.request.body).toEqual({ auto_backup_enabled: false });
    req.flush({ auto_backup_enabled: false });
    fixture.detectChanges();

    const checkbox: HTMLInputElement = fixture.nativeElement.querySelector('input[type="checkbox"]');
    expect(checkbox.checked).toBe(false);
  });
});

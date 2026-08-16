import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { Theme } from '../../../core/models';
import { ThemeList } from './theme-list';

describe('ThemeList', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ThemeList],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('renders the themes returned by the API', () => {
    const fixture = TestBed.createComponent(ThemeList);
    fixture.detectChanges();

    const themes: Theme[] = [{ id: 1, title: 'Remote work', created_at: '2026-01-01T00:00:00Z' }];
    httpMock.expectOne('/api/themes').flush(themes);
    fixture.detectChanges();

    const items = fixture.nativeElement.querySelectorAll('li');
    expect(items.length).toBe(1);
    expect(items[0].textContent).toContain('Remote work');
  });

  it('shows an empty state when there are no themes', () => {
    const fixture = TestBed.createComponent(ThemeList);
    fixture.detectChanges();

    httpMock.expectOne('/api/themes').flush([]);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.empty')?.textContent).toContain('No themes yet');
  });
});

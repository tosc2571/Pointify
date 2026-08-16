import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { provideRouter } from '@angular/router';

import { ThemeDetail } from '../../../core/models';
import { ThemeDetailPage } from './theme-detail';

describe('ThemeDetailPage', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ThemeDetailPage],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap({ id: '1' }) } },
        },
      ],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('renders theme stats and subthemes', () => {
    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      stats: { total_points: 1, avg_rating: 4, pro_count: 1, contra_count: 0 },
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [] }],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('h1').textContent).toContain('Coffee vs tea');
    expect(fixture.nativeElement.querySelector('.subtheme-title').textContent).toContain('Health');
  });

  it('shows a not-found message on 404', () => {
    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    httpMock.expectOne('/api/themes/1').flush(null, { status: 404, statusText: 'Not Found' });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.empty')?.textContent).toContain('Theme not found');
  });
});

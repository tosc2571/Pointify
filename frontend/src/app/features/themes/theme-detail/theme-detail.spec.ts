import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { provideRouter } from '@angular/router';
import { vi } from 'vitest';

import { AuthService } from '../../../core/auth.service';
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
      owner_id: 1,
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

  it('adds a point to a subtheme and reloads the theme', () => {
    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [] }],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    const addPointButton: HTMLButtonElement = Array.from(
      fixture.nativeElement.querySelectorAll('.subtheme-header .link-button'),
    ).find((el) => (el as HTMLButtonElement).textContent?.includes('Add point')) as HTMLButtonElement;
    addPointButton.click();
    fixture.detectChanges();

    const instance = fixture.componentInstance as unknown as {
      pointForm: { setValue: (v: unknown) => void };
    };
    instance.pointForm.setValue({ type: 'pro', text: 'Antioxidants', rating: 4 });
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.new-point').dispatchEvent(new Event('submit'));

    const createReq = httpMock.expectOne('/api/subthemes/1/points');
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.body).toEqual({ type: 'pro', text: 'Antioxidants', rating: 4 });
    createReq.flush({
      id: 1,
      subtheme_id: 1,
      user_id: 1,
      type: 'pro',
      text: 'Antioxidants',
      rating: 4,
      created_at: '2026-01-01T00:00:00Z',
    });

    httpMock.expectOne('/api/themes/1').flush({
      ...theme,
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [{ id: 1, subtheme_id: 1, user_id: 1, type: 'pro', text: 'Antioxidants', rating: 4, created_at: '2026-01-01T00:00:00Z' }] }],
    });
  });

  it('shows the sharing section (and loads shares) only for the owner', () => {
    const auth = TestBed.inject(AuthService);
    auth.login('alice', 'hunter2').subscribe();
    httpMock.expectOne('/api/auth/login').flush({ id: 1, username: 'alice', is_admin: false });

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    httpMock.expectOne('/api/themes/1/shares').flush([{ user_id: 2, username: 'bob' }]);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.sharing')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('.shares')?.textContent).toContain('bob');
  });

  it('hides the sharing section for a non-owner', () => {
    const auth = TestBed.inject(AuthService);
    auth.login('bob', 'hunter2').subscribe();
    httpMock.expectOne('/api/auth/login').flush({ id: 2, username: 'bob', is_admin: false });

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.sharing')).toBeFalsy();
  });

  it('requests the Markdown export and triggers a download', () => {
    const createObjectURL = vi.fn(() => 'blob:mock-url');
    const revokeObjectURL = vi.fn();
    URL.createObjectURL = createObjectURL;
    URL.revokeObjectURL = revokeObjectURL;
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    fixture.nativeElement.querySelector('.export-button').click();

    const req = httpMock.expectOne('/api/themes/1/export');
    expect(req.request.method).toBe('GET');
    req.flush('# Coffee vs tea\n');

    expect(createObjectURL).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url');

    clickSpy.mockRestore();
  });

  it('renames the theme title', () => {
    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    fixture.nativeElement.querySelector('.title-actions .link-button').click();
    fixture.detectChanges();

    const instance = fixture.componentInstance as unknown as {
      titleForm: { setValue: (v: unknown) => void };
    };
    instance.titleForm.setValue({ title: 'Coffee vs tea (revised)' });
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.title-edit').dispatchEvent(new Event('submit'));

    const req = httpMock.expectOne('/api/themes/1');
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ title: 'Coffee vs tea (revised)' });
    req.flush({ ...theme, title: 'Coffee vs tea (revised)' });

    httpMock.expectOne('/api/themes/1').flush({ ...theme, title: 'Coffee vs tea (revised)' });
  });

  it('deletes the theme after confirmation and navigates back to the list', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    const router = TestBed.inject(Router);
    const navigateSpy = vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);

    const auth = TestBed.inject(AuthService);
    auth.login('alice', 'hunter2').subscribe();
    httpMock.expectOne('/api/auth/login').flush({ id: 1, username: 'alice', is_admin: false });

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    httpMock.expectOne('/api/themes/1/shares').flush([]);
    fixture.detectChanges();

    const deleteButton: HTMLButtonElement = Array.from(
      fixture.nativeElement.querySelectorAll('.title-actions .link-button'),
    ).find((el) => (el as HTMLButtonElement).textContent?.includes('Delete')) as HTMLButtonElement;
    deleteButton.click();

    httpMock.expectOne('/api/themes/1').flush(null, { status: 204, statusText: 'No Content' });

    expect(navigateSpy).toHaveBeenCalledWith('/themes');
  });

  it('renames and deletes a subtheme', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 0, avg_rating: 0, pro_count: 0, contra_count: 0 },
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [] }],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    const renameButton: HTMLButtonElement = Array.from(
      fixture.nativeElement.querySelectorAll('.subtheme-actions .link-button'),
    ).find((el) => (el as HTMLButtonElement).textContent?.includes('Rename')) as HTMLButtonElement;
    renameButton.click();
    fixture.detectChanges();

    const instance = fixture.componentInstance as unknown as {
      subthemeEditForm: { setValue: (v: unknown) => void };
    };
    instance.subthemeEditForm.setValue({ title: 'Wellbeing' });
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.subtheme-edit').dispatchEvent(new Event('submit'));

    let req = httpMock.expectOne('/api/themes/1/subthemes/1');
    expect(req.request.method).toBe('PATCH');
    req.flush({ id: 1, title: 'Wellbeing', theme_id: 1 });
    httpMock.expectOne('/api/themes/1').flush({
      ...theme,
      subthemes: [{ id: 1, title: 'Wellbeing', theme_id: 1, points: [] }],
    });
    fixture.detectChanges();

    const deleteButton: HTMLButtonElement = Array.from(
      fixture.nativeElement.querySelectorAll('.subtheme-actions .link-button'),
    ).find((el) => (el as HTMLButtonElement).textContent?.includes('Delete')) as HTMLButtonElement;
    deleteButton.click();

    req = httpMock.expectOne('/api/themes/1/subthemes/1');
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });
    httpMock.expectOne('/api/themes/1').flush({ ...theme, subthemes: [] });
  });

  it('edits and deletes a point', () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    const fixture = TestBed.createComponent(ThemeDetailPage);
    fixture.detectChanges();

    const point = {
      id: 1,
      subtheme_id: 1,
      user_id: 1,
      type: 'pro' as const,
      text: 'Antioxidants',
      rating: 4,
      created_at: '2026-01-01T00:00:00Z',
    };
    const theme: ThemeDetail = {
      id: 1,
      title: 'Coffee vs tea',
      created_at: '2026-01-01T00:00:00Z',
      owner_id: 1,
      stats: { total_points: 1, avg_rating: 4, pro_count: 1, contra_count: 0 },
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [point] }],
    };
    httpMock.expectOne('/api/themes/1').flush(theme);
    fixture.detectChanges();

    fixture.nativeElement.querySelector('.point-actions .link-button').click();
    fixture.detectChanges();

    const instance = fixture.componentInstance as unknown as {
      pointEditForm: { setValue: (v: unknown) => void };
    };
    instance.pointEditForm.setValue({ type: 'contra', text: 'Actually jittery', rating: 2 });
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.new-point').dispatchEvent(new Event('submit'));

    let req = httpMock.expectOne('/api/subthemes/1/points/1');
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ type: 'contra', text: 'Actually jittery', rating: 2 });
    const updatedPoint = { ...point, type: 'contra', text: 'Actually jittery', rating: 2 };
    req.flush(updatedPoint);
    httpMock.expectOne('/api/themes/1').flush({
      ...theme,
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [updatedPoint] }],
    });
    fixture.detectChanges();

    const deleteButton: HTMLButtonElement = Array.from(
      fixture.nativeElement.querySelectorAll('.point-actions .link-button'),
    ).find((el) => (el as HTMLButtonElement).textContent?.includes('Delete')) as HTMLButtonElement;
    deleteButton.click();

    req = httpMock.expectOne('/api/subthemes/1/points/1');
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });
    httpMock.expectOne('/api/themes/1').flush({
      ...theme,
      subthemes: [{ id: 1, title: 'Health', theme_id: 1, points: [] }],
    });
  });
});

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { SubTheme, Theme, ThemeDetail } from '../../core/models';

@Injectable({ providedIn: 'root' })
export class ThemesService {
  constructor(private readonly http: HttpClient) {}

  list(): Observable<Theme[]> {
    return this.http.get<Theme[]>('/api/themes');
  }

  get(id: number): Observable<ThemeDetail> {
    return this.http.get<ThemeDetail>(`/api/themes/${id}`);
  }

  create(title: string): Observable<Theme> {
    return this.http.post<Theme>('/api/themes', { title });
  }

  createSubtheme(themeId: number, title: string): Observable<SubTheme> {
    return this.http.post<SubTheme>(`/api/themes/${themeId}/subthemes`, { title });
  }
}

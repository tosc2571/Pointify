import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Share, SubTheme, Theme, ThemeDetail } from '../../core/models';

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

  listShares(themeId: number): Observable<Share[]> {
    return this.http.get<Share[]>(`/api/themes/${themeId}/shares`);
  }

  share(themeId: number, username: string): Observable<Share> {
    return this.http.post<Share>(`/api/themes/${themeId}/shares`, { username });
  }

  revokeShare(themeId: number, userId: number): Observable<void> {
    return this.http.delete<void>(`/api/themes/${themeId}/shares/${userId}`);
  }

  exportMarkdown(themeId: number): Observable<string> {
    return this.http.get(`/api/themes/${themeId}/export`, { responseType: 'text' });
  }
}

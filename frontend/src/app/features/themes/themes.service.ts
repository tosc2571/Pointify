import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Theme } from '../../core/models';

@Injectable({ providedIn: 'root' })
export class ThemesService {
  constructor(private readonly http: HttpClient) {}

  list(): Observable<Theme[]> {
    return this.http.get<Theme[]>('/api/themes');
  }
}

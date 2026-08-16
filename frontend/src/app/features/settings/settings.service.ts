import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Settings } from '../../core/models';

@Injectable({ providedIn: 'root' })
export class SettingsService {
  constructor(private readonly http: HttpClient) {}

  get(): Observable<Settings> {
    return this.http.get<Settings>('/api/settings');
  }

  update(autoBackupEnabled: boolean): Observable<Settings> {
    return this.http.put<Settings>('/api/settings', { auto_backup_enabled: autoBackupEnabled });
  }
}

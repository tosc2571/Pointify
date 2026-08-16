import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, catchError, of, tap } from 'rxjs';

import { User } from './models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly currentUserSignal = signal<User | null>(null);
  readonly currentUser = this.currentUserSignal.asReadonly();

  constructor(private readonly http: HttpClient) {}

  bootstrap(): Observable<User | null> {
    return this.http.get<User>('/api/auth/me').pipe(
      tap((user) => this.currentUserSignal.set(user)),
      catchError(() => {
        this.currentUserSignal.set(null);
        return of(null);
      }),
    );
  }

  login(username: string, password: string): Observable<User> {
    return this.http
      .post<User>('/api/auth/login', { username, password })
      .pipe(tap((user) => this.currentUserSignal.set(user)));
  }

  register(username: string, password: string): Observable<User> {
    return this.http.post<User>('/api/auth/register', { username, password });
  }

  logout(): Observable<void> {
    return this.http
      .post<void>('/api/auth/logout', {})
      .pipe(tap(() => this.currentUserSignal.set(null)));
  }
}

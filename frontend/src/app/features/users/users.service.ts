import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { User } from '../../core/models';

export interface UserCreatePayload {
  username: string;
  password: string;
  is_admin: boolean;
}

@Injectable({ providedIn: 'root' })
export class UsersService {
  constructor(private readonly http: HttpClient) {}

  list(): Observable<User[]> {
    return this.http.get<User[]>('/api/admin/users');
  }

  create(payload: UserCreatePayload): Observable<User> {
    return this.http.post<User>('/api/admin/users', payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`/api/admin/users/${id}`);
  }
}

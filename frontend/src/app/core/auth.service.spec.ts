import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AuthService } from './auth.service';
import { User } from './models';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  const user: User = { id: 1, username: 'alice', is_admin: false };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('sets currentUser on successful bootstrap', () => {
    service.bootstrap().subscribe();
    httpMock.expectOne('/api/auth/me').flush(user);
    expect(service.currentUser()).toEqual(user);
  });

  it('clears currentUser when bootstrap fails (not logged in)', () => {
    service.bootstrap().subscribe();
    httpMock.expectOne('/api/auth/me').flush(null, { status: 401, statusText: 'Unauthorized' });
    expect(service.currentUser()).toBeNull();
  });

  it('sets currentUser on successful login', () => {
    service.login('alice', 'hunter2').subscribe();
    const req = httpMock.expectOne('/api/auth/login');
    expect(req.request.body).toEqual({ username: 'alice', password: 'hunter2' });
    req.flush(user);
    expect(service.currentUser()).toEqual(user);
  });

  it('clears currentUser on logout', () => {
    service.login('alice', 'hunter2').subscribe();
    httpMock.expectOne('/api/auth/login').flush(user);

    service.logout().subscribe();
    httpMock.expectOne('/api/auth/logout').flush(null);
    expect(service.currentUser()).toBeNull();
  });
});

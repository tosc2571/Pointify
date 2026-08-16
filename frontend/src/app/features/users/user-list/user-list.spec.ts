import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AuthService } from '../../../core/auth.service';
import { User } from '../../../core/models';
import { UserList } from './user-list';

describe('UserList', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserList],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('renders users and disables delete for the current user', () => {
    const auth = TestBed.inject(AuthService);
    auth.login('admin', 'hunter2').subscribe();
    httpMock.expectOne('/api/auth/login').flush({ id: 1, username: 'admin', is_admin: true });

    const fixture = TestBed.createComponent(UserList);
    fixture.detectChanges();

    const users: User[] = [
      { id: 1, username: 'admin', is_admin: true },
      { id: 2, username: 'bob', is_admin: false },
    ];
    httpMock.expectOne('/api/admin/users').flush(users);
    fixture.detectChanges();

    const rows = fixture.nativeElement.querySelectorAll('li');
    expect(rows.length).toBe(2);
    const deleteButtons = fixture.nativeElement.querySelectorAll('.delete-button');
    expect(deleteButtons[0].disabled).toBe(true);
    expect(deleteButtons[1].disabled).toBe(false);
  });

  it('creates a user and reloads the list', () => {
    const fixture = TestBed.createComponent(UserList);
    fixture.detectChanges();
    httpMock.expectOne('/api/admin/users').flush([]);
    fixture.detectChanges();

    const instance = fixture.componentInstance as unknown as {
      form: { setValue: (v: unknown) => void };
    };
    instance.form.setValue({ username: 'newuser', password: 'pw123456', is_admin: false });
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.new-user').dispatchEvent(new Event('submit'));

    const createReq = httpMock.expectOne('/api/admin/users');
    expect(createReq.request.method).toBe('POST');
    createReq.flush({ id: 2, username: 'newuser', is_admin: false });

    httpMock.expectOne('/api/admin/users').flush([{ id: 2, username: 'newuser', is_admin: false }]);
  });
});

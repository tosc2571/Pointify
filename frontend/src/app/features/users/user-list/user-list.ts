import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { AuthService } from '../../../core/auth.service';
import { User } from '../../../core/models';
import { UsersService } from '../users.service';

@Component({
  selector: 'app-user-list',
  imports: [ReactiveFormsModule],
  templateUrl: './user-list.html',
  styleUrl: './user-list.css',
})
export class UserList implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly usersService = inject(UsersService);
  private readonly auth = inject(AuthService);

  protected readonly currentUser = this.auth.currentUser;
  protected readonly users = signal<User[]>([]);
  protected readonly loading = signal(true);
  protected readonly creating = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', [Validators.required, Validators.maxLength(72)]],
    is_admin: [false],
  });

  ngOnInit(): void {
    this.loadUsers();
  }

  private loadUsers(): void {
    this.loading.set(true);
    this.usersService.list().subscribe({
      next: (users) => {
        this.users.set(users);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  submit(): void {
    if (this.form.invalid) {
      return;
    }
    this.creating.set(true);
    this.error.set(null);
    this.usersService.create(this.form.getRawValue()).subscribe({
      next: () => {
        this.form.reset({ username: '', password: '', is_admin: false });
        this.creating.set(false);
        this.loadUsers();
      },
      error: () => {
        this.error.set('Could not create user (username may already exist).');
        this.creating.set(false);
      },
    });
  }

  deleteUser(id: number): void {
    this.usersService.delete(id).subscribe({
      next: () => this.loadUsers(),
    });
  }
}

import { Routes } from '@angular/router';

import { adminGuard } from './core/admin.guard';
import { authGuard } from './core/auth.guard';
import { Shell } from './shared/layout/shell';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register').then((m) => m.Register),
  },
  {
    path: '',
    component: Shell,
    canActivate: [authGuard],
    children: [
      {
        path: 'themes',
        loadComponent: () =>
          import('./features/themes/theme-list/theme-list').then((m) => m.ThemeList),
      },
      {
        path: 'themes/:id',
        loadComponent: () =>
          import('./features/themes/theme-detail/theme-detail').then((m) => m.ThemeDetailPage),
      },
      {
        path: 'admin/users',
        canActivate: [adminGuard],
        loadComponent: () => import('./features/users/user-list/user-list').then((m) => m.UserList),
      },
      {
        path: 'admin/settings',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./features/settings/settings-page/settings-page').then((m) => m.SettingsPage),
      },
      { path: '', pathMatch: 'full', redirectTo: 'themes' },
    ],
  },
  { path: '**', redirectTo: 'login' },
];

import { Routes } from '@angular/router';

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
      { path: '', pathMatch: 'full', redirectTo: 'themes' },
    ],
  },
  { path: '**', redirectTo: 'login' },
];

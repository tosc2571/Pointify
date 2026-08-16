import { Component, OnInit, signal } from '@angular/core';

import { Theme } from '../../../core/models';
import { ThemesService } from '../themes.service';

@Component({
  selector: 'app-theme-list',
  imports: [],
  templateUrl: './theme-list.html',
  styleUrl: './theme-list.css',
})
export class ThemeList implements OnInit {
  protected readonly themes = signal<Theme[]>([]);
  protected readonly loading = signal(true);

  constructor(private readonly themesService: ThemesService) {}

  ngOnInit(): void {
    this.themesService.list().subscribe({
      next: (themes) => {
        this.themes.set(themes);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}

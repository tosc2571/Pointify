import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { Theme } from '../../../core/models';
import { ThemesService } from '../themes.service';

@Component({
  selector: 'app-theme-list',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './theme-list.html',
  styleUrl: './theme-list.css',
})
export class ThemeList implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly themesService = inject(ThemesService);

  protected readonly themes = signal<Theme[]>([]);
  protected readonly loading = signal(true);
  protected readonly creating = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  ngOnInit(): void {
    this.loadThemes();
  }

  private loadThemes(): void {
    this.loading.set(true);
    this.themesService.list().subscribe({
      next: (themes) => {
        this.themes.set(themes);
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
    const { title } = this.form.getRawValue();
    this.themesService.create(title).subscribe({
      next: () => {
        this.form.reset({ title: '' });
        this.creating.set(false);
        this.loadThemes();
      },
      error: () => this.creating.set(false),
    });
  }
}

import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ThemeDetail } from '../../../core/models';
import { ThemesService } from '../themes.service';

@Component({
  selector: 'app-theme-detail',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './theme-detail.html',
  styleUrl: './theme-detail.css',
})
export class ThemeDetailPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);
  private readonly themesService = inject(ThemesService);

  protected readonly theme = signal<ThemeDetail | null>(null);
  protected readonly loading = signal(true);
  protected readonly notFound = signal(false);
  protected readonly creatingSubtheme = signal(false);

  protected readonly subthemeForm = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  private themeId!: number;

  ngOnInit(): void {
    this.themeId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadTheme();
  }

  private loadTheme(): void {
    this.loading.set(true);
    this.themesService.get(this.themeId).subscribe({
      next: (theme) => {
        this.theme.set(theme);
        this.loading.set(false);
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }

  submitSubtheme(): void {
    if (this.subthemeForm.invalid) {
      return;
    }
    this.creatingSubtheme.set(true);
    const { title } = this.subthemeForm.getRawValue();
    this.themesService.createSubtheme(this.themeId, title).subscribe({
      next: () => {
        this.subthemeForm.reset({ title: '' });
        this.creatingSubtheme.set(false);
        this.loadTheme();
      },
      error: () => this.creatingSubtheme.set(false),
    });
  }
}

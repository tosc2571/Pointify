import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { PointType, ThemeDetail } from '../../../core/models';
import { PointsService } from '../../points/points.service';
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
  private readonly pointsService = inject(PointsService);

  protected readonly theme = signal<ThemeDetail | null>(null);
  protected readonly loading = signal(true);
  protected readonly notFound = signal(false);
  protected readonly creatingSubtheme = signal(false);
  protected readonly expandedSubthemeId = signal<number | null>(null);
  protected readonly creatingPoint = signal(false);

  protected readonly subthemeForm = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  protected readonly pointForm = this.fb.nonNullable.group({
    type: ['pro' as PointType, Validators.required],
    text: ['', Validators.required],
    rating: [3, [Validators.required, Validators.min(1), Validators.max(5)]],
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

  toggleAddPoint(subthemeId: number): void {
    if (this.expandedSubthemeId() === subthemeId) {
      this.expandedSubthemeId.set(null);
      return;
    }
    this.pointForm.reset({ type: 'pro', text: '', rating: 3 });
    this.expandedSubthemeId.set(subthemeId);
  }

  submitPoint(subthemeId: number): void {
    if (this.pointForm.invalid) {
      return;
    }
    this.creatingPoint.set(true);
    const { type, text, rating } = this.pointForm.getRawValue();
    this.pointsService.create(subthemeId, { type, text, rating }).subscribe({
      next: () => {
        this.creatingPoint.set(false);
        this.expandedSubthemeId.set(null);
        this.loadTheme();
      },
      error: () => this.creatingPoint.set(false),
    });
  }
}

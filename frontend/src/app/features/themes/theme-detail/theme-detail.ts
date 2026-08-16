import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/auth.service';
import { PointType, Share, ThemeDetail } from '../../../core/models';
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
  private readonly auth = inject(AuthService);

  protected readonly theme = signal<ThemeDetail | null>(null);
  protected readonly loading = signal(true);
  protected readonly notFound = signal(false);
  protected readonly creatingSubtheme = signal(false);
  protected readonly expandedSubthemeId = signal<number | null>(null);
  protected readonly creatingPoint = signal(false);

  protected readonly isOwner = computed(() => this.theme()?.owner_id === this.auth.currentUser()?.id);
  protected readonly shares = signal<Share[]>([]);
  protected readonly sharingBusy = signal(false);
  protected readonly shareError = signal<string | null>(null);

  protected readonly subthemeForm = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  protected readonly pointForm = this.fb.nonNullable.group({
    type: ['pro' as PointType, Validators.required],
    text: ['', Validators.required],
    rating: [3, [Validators.required, Validators.min(1), Validators.max(5)]],
  });

  protected readonly shareForm = this.fb.nonNullable.group({
    username: ['', Validators.required],
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
        if (this.isOwner()) {
          this.loadShares();
        }
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }

  private loadShares(): void {
    this.themesService.listShares(this.themeId).subscribe({
      next: (shares) => this.shares.set(shares),
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

  submitShare(): void {
    if (this.shareForm.invalid) {
      return;
    }
    this.sharingBusy.set(true);
    this.shareError.set(null);
    const { username } = this.shareForm.getRawValue();
    this.themesService.share(this.themeId, username).subscribe({
      next: () => {
        this.shareForm.reset({ username: '' });
        this.sharingBusy.set(false);
        this.loadShares();
      },
      error: () => {
        this.shareError.set('Could not share (user may not exist or already has access).');
        this.sharingBusy.set(false);
      },
    });
  }

  revokeShare(userId: number): void {
    this.themesService.revokeShare(this.themeId, userId).subscribe({
      next: () => this.loadShares(),
    });
  }

  exportMarkdown(): void {
    this.themesService.exportMarkdown(this.themeId).subscribe((markdown) => {
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${this.theme()?.title ?? 'theme'}.md`;
      link.click();
      URL.revokeObjectURL(url);
    });
  }
}

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/auth.service';
import { Point, PointType, Share, ThemeDetail } from '../../../core/models';
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
  private readonly router = inject(Router);
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

  protected readonly editingTitle = signal(false);
  protected readonly editingSubthemeId = signal<number | null>(null);
  protected readonly editingPointId = signal<number | null>(null);

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

  protected readonly titleForm = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  protected readonly subthemeEditForm = this.fb.nonNullable.group({
    title: ['', Validators.required],
  });

  protected readonly pointEditForm = this.fb.nonNullable.group({
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

  // --- theme title / delete ---

  startEditTitle(): void {
    this.titleForm.setValue({ title: this.theme()?.title ?? '' });
    this.editingTitle.set(true);
  }

  cancelEditTitle(): void {
    this.editingTitle.set(false);
  }

  submitTitleEdit(): void {
    if (this.titleForm.invalid) {
      return;
    }
    const { title } = this.titleForm.getRawValue();
    this.themesService.update(this.themeId, title).subscribe({
      next: () => {
        this.editingTitle.set(false);
        this.loadTheme();
      },
    });
  }

  deleteTheme(): void {
    const title = this.theme()?.title ?? 'this theme';
    if (!confirm(`Delete "${title}"? This removes all its subthemes and points and cannot be undone.`)) {
      return;
    }
    this.themesService.delete(this.themeId).subscribe({
      next: () => this.router.navigateByUrl('/themes'),
    });
  }

  // --- subthemes ---

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

  startEditSubtheme(subthemeId: number, currentTitle: string): void {
    this.subthemeEditForm.setValue({ title: currentTitle });
    this.editingSubthemeId.set(subthemeId);
  }

  cancelEditSubtheme(): void {
    this.editingSubthemeId.set(null);
  }

  submitSubthemeEdit(subthemeId: number): void {
    if (this.subthemeEditForm.invalid) {
      return;
    }
    const { title } = this.subthemeEditForm.getRawValue();
    this.themesService.updateSubtheme(this.themeId, subthemeId, title).subscribe({
      next: () => {
        this.editingSubthemeId.set(null);
        this.loadTheme();
      },
    });
  }

  deleteSubtheme(subthemeId: number, title: string): void {
    if (!confirm(`Delete subtheme "${title}"? This removes all its points and cannot be undone.`)) {
      return;
    }
    this.themesService.deleteSubtheme(this.themeId, subthemeId).subscribe({
      next: () => this.loadTheme(),
    });
  }

  // --- points ---

  toggleAddPoint(subthemeId: number): void {
    if (this.expandedSubthemeId() === subthemeId) {
      this.expandedSubthemeId.set(null);
      return;
    }
    this.editingPointId.set(null);
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

  startEditPoint(point: Point): void {
    this.expandedSubthemeId.set(null);
    this.pointEditForm.setValue({ type: point.type, text: point.text, rating: point.rating });
    this.editingPointId.set(point.id);
  }

  cancelEditPoint(): void {
    this.editingPointId.set(null);
  }

  submitPointEdit(subthemeId: number, pointId: number): void {
    if (this.pointEditForm.invalid) {
      return;
    }
    const { type, text, rating } = this.pointEditForm.getRawValue();
    this.pointsService.update(subthemeId, pointId, { type, text, rating }).subscribe({
      next: () => {
        this.editingPointId.set(null);
        this.loadTheme();
      },
    });
  }

  deletePoint(subthemeId: number, pointId: number): void {
    if (!confirm('Delete this point? This cannot be undone.')) {
      return;
    }
    this.pointsService.delete(subthemeId, pointId).subscribe({
      next: () => this.loadTheme(),
    });
  }

  // --- sharing ---

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

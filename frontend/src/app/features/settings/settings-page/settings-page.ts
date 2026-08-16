import { Component, OnInit, inject, signal } from '@angular/core';

import { Settings } from '../../../core/models';
import { SettingsService } from '../settings.service';

@Component({
  selector: 'app-settings-page',
  imports: [],
  templateUrl: './settings-page.html',
  styleUrl: './settings-page.css',
})
export class SettingsPage implements OnInit {
  private readonly settingsService = inject(SettingsService);

  protected readonly settings = signal<Settings | null>(null);

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.settingsService.get().subscribe((s) => this.settings.set(s));
  }

  toggleAutoBackup(): void {
    const current = this.settings();
    if (!current) {
      return;
    }
    this.settingsService.update(!current.auto_backup_enabled).subscribe((s) => this.settings.set(s));
  }
}

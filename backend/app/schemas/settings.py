from pydantic import BaseModel


class SettingsOut(BaseModel):
    auto_backup_enabled: bool


class SettingsUpdate(BaseModel):
    auto_backup_enabled: bool

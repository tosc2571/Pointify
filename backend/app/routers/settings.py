from fastapi import APIRouter, Depends

from app.dependencies import get_db_path, require_admin
from app.schemas.settings import SettingsOut, SettingsUpdate
from app.services.settings_store import AppSettings, load_settings, save_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def get_settings_endpoint(admin=Depends(require_admin), db_path: str = Depends(get_db_path)):
    settings = load_settings(db_path)
    return SettingsOut(auto_backup_enabled=settings.auto_backup_enabled)


@router.put("", response_model=SettingsOut)
def update_settings_endpoint(
    payload: SettingsUpdate,
    admin=Depends(require_admin),
    db_path: str = Depends(get_db_path),
):
    settings = AppSettings(auto_backup_enabled=payload.auto_backup_enabled)
    save_settings(db_path, settings)
    return SettingsOut(auto_backup_enabled=settings.auto_backup_enabled)

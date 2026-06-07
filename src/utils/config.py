import os
from pathlib import Path

APP_TITLE = "Gestion d'École"

BASE_DIR = Path(__file__).resolve().parents[2]
APPDATA_DIR = Path(os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming")))
DATA_DIR = APPDATA_DIR / "EcoleManager"
DB_PATH = str(DATA_DIR / "ecole.db")

# Google Drive OAuth credential & token paths (stored under app data)
GDRIVE_CREDENTIALS_PATH = str(DATA_DIR / "gdrive_credentials.json")
GDRIVE_TOKEN_PATH = str(DATA_DIR / "gdrive_token.json")

# Legacy paths (older versions stored data alongside the app)
LEGACY_DATA_DIR = BASE_DIR / "data"
LEGACY_DB_PATH = str(LEGACY_DATA_DIR / "ecole.db")
LEGACY_SETTINGS_PATH = LEGACY_DATA_DIR / "app_settings.json"

SETTINGS_PATH = DATA_DIR / "app_settings.json"

_DEFAULT_SETTINGS = {
    "school_name": "École Manager",
    "dark_mode": False,
    "academic_year": "2024-2025"
}

def _migrate_legacy_files_if_needed() -> None:
    """Move legacy DB and settings from app folder to AppData if present."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Migrate DB
        if os.path.exists(LEGACY_DB_PATH) and not os.path.exists(DB_PATH):
            try:
                import shutil
                shutil.move(LEGACY_DB_PATH, DB_PATH)
            except Exception:
                pass
        # Migrate settings
        if os.path.exists(LEGACY_SETTINGS_PATH) and not SETTINGS_PATH.exists():
            try:
                import shutil
                shutil.move(str(LEGACY_SETTINGS_PATH), str(SETTINGS_PATH))
            except Exception:
                pass
    except Exception:
        pass


def load_settings() -> dict:
    _migrate_legacy_files_if_needed()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            import json
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return dict(_DEFAULT_SETTINGS)
    return dict(_DEFAULT_SETTINGS)

def save_settings(settings: dict) -> None:
    _migrate_legacy_files_if_needed()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    import json
    SETTINGS_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
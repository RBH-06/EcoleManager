from pathlib import Path
import sys

def get_resource_path(relative_path: str) -> str:
    """Return an absolute path to a resource.
    Works in development and when bundled with PyInstaller (via _MEIPASS).
    relative_path should be relative to the project root when in dev.
    Example: get_resource_path('src/assets/favicon.ico')
    """
    try:
        base = getattr(sys, "_MEIPASS", None)
    except Exception:
        base = None
    if base:
        return str(Path(base) / relative_path)
    # Dev: project root is two levels up from utils/ (repo root)
    return str(Path(__file__).resolve().parents[2] / relative_path)
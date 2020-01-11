
from pathlib import Path


def _locate_app_path():
    p = Path.cwd()
    parent = p.parent

    while p != parent:
        bgme_path = p / '.bugme'
        if bgme_path.exists():
            return bgme_path
        p = parent
        parent = p.parent

    return None


_app_path = _locate_app_path()

APP_PATH = _app_path
if _app_path is not None:
    DB_PATH = _app_path / "bugs.db"
else:
    DB_PATH = None


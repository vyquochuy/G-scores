import sys
from pathlib import Path

# Bổ sung thư mục backend vào sys.path để import các module trong app
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa: F401

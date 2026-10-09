"""Делает пакет из src/ доступным для импорта в тестах."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

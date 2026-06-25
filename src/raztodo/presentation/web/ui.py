from __future__ import annotations

from pathlib import Path

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_index_html() -> str:
    """Return the single-page web UI."""
    return (_TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

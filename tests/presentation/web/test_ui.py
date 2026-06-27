from pathlib import Path

from raztodo.presentation.web.ui import render_index_html


def test_render_index_html(monkeypatch):
    expected = "<html><body>Hello</body></html>"

    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding: expected,
    )

    assert render_index_html() == expected

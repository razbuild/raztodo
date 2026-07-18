from __future__ import annotations

import re
from pathlib import Path

import pytest

_CSS_FILE = (
    Path(__file__).parents[3]
    / "src"
    / "raztodo"
    / "presentation"
    / "web"
    / "static"
    / "css"
    / "style.css"
)


def _css_block(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\}}", css, re.DOTALL)
    assert match is not None, f"Missing CSS block for {selector}"
    return match.group("body")


def _variables(block: str) -> dict[str, str]:
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block))


def _relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize(
    ("background", "foreground"),
    [
        ("--ph-bg", "--ph-text"),
        ("--pm-bg", "--pm-text"),
        ("--pl-bg", "--pl-text"),
        ("--tag-bg", "--tag-text"),
        ("--project-bg", "--project-text"),
        ("--overdue-bg", "--overdue-text"),
    ],
)
def test_light_theme_badges_meet_text_contrast(background: str, foreground: str) -> None:
    css = _CSS_FILE.read_text()
    light_variables = _variables(_css_block(css, '[data-theme="light"]'))

    assert background in light_variables
    assert foreground in light_variables
    assert _contrast_ratio(light_variables[background], light_variables[foreground]) >= 4.5


def test_overdue_badge_uses_theme_tokens() -> None:
    css = _CSS_FILE.read_text()
    overdue = _css_block(css, ".badge.overdue")

    assert "background: var(--overdue-bg);" in overdue
    assert "color: var(--overdue-text);" in overdue

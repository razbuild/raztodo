import ctypes
import os
import sys
from collections.abc import Callable
from typing import ClassVar


class Colorizer:
    COLORS: ClassVar[dict[str, str]] = {
        "BLACK": "30",
        "RED": "31",
        "GREEN": "32",
        "YELLOW": "33",
        "BLUE": "34",
        "MAGENTA": "35",
        "CYAN": "36",
        "WHITE": "37",
        "GRAY": "90",
    }

    ICONS: ClassVar[dict[str, dict[str, str]]] = {
        "ok": {"nerd": "", "std": "✓", "ascii": "[OK]", "color": "GREEN"},
        "err": {"nerd": "", "std": "✗", "ascii": "[ERR]", "color": "RED"},
        "warn": {"nerd": "", "std": "!", "ascii": "[WARN]", "color": "YELLOW"},
        "info": {"nerd": "󰙎", "std": "i", "ascii": "[INFO]", "color": "BLUE"},
    }

    ok: Callable[[], str]
    err: Callable[[], str]
    warn: Callable[[], str]
    info: Callable[[], str]

    black: Callable[[str], str]
    red: Callable[[str], str]
    green: Callable[[str], str]
    yellow: Callable[[str], str]
    blue: Callable[[str], str]
    magenta: Callable[[str], str]
    cyan: Callable[[str], str]
    white: Callable[[str], str]
    gray: Callable[[str], str]

    def __init__(self) -> None:
        self.use_color: bool = self._supports_color()
        self.icon_mode: str = self._get_icon_mode()

        for name, code in self.COLORS.items():
            setattr(self, name.lower(), self._make_color_func(code))

        for name, data in self.ICONS.items():
            color_key = data.get("color", "WHITE")
            color_code = self.COLORS.get(color_key, "37")
            setattr(
                self,
                name,
                self._make_icon_func(data, color_code),
            )

    def _make_color_func(self, code: str) -> Callable[[str], str]:
        return lambda text: self.color(text, code)

    def _make_icon_func(self, data: dict[str, str], code: str) -> Callable[[], str]:
        def fn() -> str:
            if self.icon_mode == "nerd":
                symbol = data["nerd"]
            elif self.icon_mode == "std":
                symbol = data["std"]
            else:
                symbol = data["ascii"]

            return self.color(symbol, code)

        return fn

    def color(self, text: str, fg_code: str) -> str:
        if not self.use_color:
            return text
        return f"\033[{fg_code}m{text}\033[0m"

    def set_color(self, enabled: bool) -> None:
        self.use_color = enabled

    def _supports_color(self) -> bool:
        if os.getenv("NO_COLOR") or os.getenv("RAZTODO_NO_COLOR"):
            return False

        force = os.getenv("RAZTODO_FORCE_COLOR", "").lower()
        if force in ("1", "true", "yes", "on"):
            return True

        stream = sys.stdout
        if not hasattr(stream, "isatty") or not stream.isatty():
            return False
        if os.name == "nt":
            return self._enable_windows_vt_mode()
        term = os.getenv("TERM", "")
        return bool(term and term.lower() != "dumb")

    def _get_icon_mode(self) -> str:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        try:
            "✓".encode(encoding)
        except Exception:
            return "ascii"

        force_nerd = os.getenv("RAZTODO_USE_NERD_ICONS", "").lower()
        if force_nerd in ("1", "true", "yes", "on"):
            return "nerd"

        if os.name == "nt":
            return "std"
        else:
            return "std"

    def _enable_windows_vt_mode(self) -> bool:
        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return False

        kernel32 = getattr(windll, "kernel32", None)
        if kernel32 is None:
            return False

        handle = kernel32.GetStdHandle(-11)
        if handle in (0, -1):
            return False

        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False

        enable_virtual_terminal_processing = 0x0004
        success = kernel32.SetConsoleMode(
            handle, mode.value | enable_virtual_terminal_processing
        )
        return bool(success)

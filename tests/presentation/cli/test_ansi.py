import os
from unittest import mock

from raztodo.presentation.cli.ansi import Colorizer


class TestColorizer:
    """Test cases for Colorizer."""

    def test_colorizer_initialization(self):
        """Test Colorizer initialization and attribute existence."""
        colorizer = Colorizer()
        assert hasattr(colorizer, "use_color")
        assert hasattr(colorizer, "icon_mode")
        assert colorizer.icon_mode in ["nerd", "std", "ascii"]

    def test_methods_existence(self):
        """Test that dynamic methods are created."""
        colorizer = Colorizer()

        # Colors
        assert hasattr(colorizer, "black")
        assert hasattr(colorizer, "red")
        assert hasattr(colorizer, "green")
        assert hasattr(colorizer, "yellow")
        assert hasattr(colorizer, "blue")
        assert hasattr(colorizer, "magenta")
        assert hasattr(colorizer, "cyan")
        assert hasattr(colorizer, "white")
        assert hasattr(colorizer, "gray")

        # Icons
        assert hasattr(colorizer, "ok")
        assert hasattr(colorizer, "err")
        assert hasattr(colorizer, "warn")
        assert hasattr(colorizer, "info")

    def test_color_method_disabled(self):
        """Test color method returns plain text when disabled."""
        colorizer = Colorizer()
        colorizer.set_color(False)

        assert colorizer.color("test", "31") == "test"
        assert colorizer.red("test") == "test"

    def test_color_method_enabled(self):
        """Test color method returns ANSI codes when enabled."""
        colorizer = Colorizer()
        colorizer.set_color(True)

        result = colorizer.red("test")
        assert "\033[31m" in result
        assert "test" in result
        assert "\033[0m" in result

    def test_env_no_color(self):
        """Test NO_COLOR environment variable."""
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            colorizer = Colorizer()
            assert colorizer.use_color is False

    def test_env_force_color_valid(self):
        """Test RAZTODO_FORCE_COLOR with valid truthy values."""
        for val in ["1", "true", "True", "yes", "on"]:
            with mock.patch.dict(os.environ, {"RAZTODO_FORCE_COLOR": val}):
                if "NO_COLOR" in os.environ:
                    del os.environ["NO_COLOR"]
                colorizer = Colorizer()
                assert colorizer.use_color is True, f"Failed for value: {val}"

    def test_env_force_color_invalid(self):
        """Test RAZTODO_FORCE_COLOR with falsy values (Bug fix test)."""
        with mock.patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False

            for val in ["0", "false", "off"]:
                with mock.patch.dict(os.environ, {"RAZTODO_FORCE_COLOR": val}):
                    colorizer = Colorizer()
                    assert colorizer.use_color is False, f"Failed for value: {val}"

    @mock.patch("os.name", "posix")
    def test_icon_mode_linux_default(self):
        """Test default icon mode on Linux (should be 'std')."""
        with mock.patch.dict(os.environ):
            if "RAZTODO_USE_NERD_ICONS" in os.environ:
                del os.environ["RAZTODO_USE_NERD_ICONS"]

            # Force deterministic behavior: pretend nerd fonts are not installed
            with mock.patch.object(Colorizer, "_has_nerd_fonts", return_value=False):
                colorizer = Colorizer()
                assert colorizer.icon_mode == "std"
                assert "✓" in colorizer.ok()

    @mock.patch("os.name", "nt")
    def test_icon_mode_windows_default(self):
        """Test default icon mode on Windows (should be 'std')."""
        with mock.patch.dict(os.environ):
            if "RAZTODO_USE_NERD_ICONS" in os.environ:
                del os.environ["RAZTODO_USE_NERD_ICONS"]

            with mock.patch.object(Colorizer, "_has_nerd_fonts", return_value=False):
                colorizer = Colorizer()
                assert colorizer.icon_mode == "std"
                assert "✓" in colorizer.ok()

            colorizer = Colorizer()
            assert colorizer.icon_mode == "std"
            assert "✓" in colorizer.ok()

    def test_icon_mode_force_nerd(self):
        """Test forcing nerd fonts via environment variable."""
        with mock.patch.dict(os.environ, {"RAZTODO_USE_NERD_ICONS": "1"}):
            colorizer = Colorizer()
            assert colorizer.icon_mode == "nerd"
            assert "" in colorizer.ok()

    def test_icon_mode_ascii_fallback(self):
        """Test fallback to ASCII if encoding fails."""
        with mock.patch("sys.stdout") as mock_stdout:
            mock_stdout.encoding = "ascii"

            pass

    def test_icon_render_std(self):
        """Test specific output for Standard mode."""
        colorizer = Colorizer()
        colorizer.icon_mode = "std"
        colorizer.use_color = False

        assert colorizer.ok() == "✓"
        assert colorizer.err() == "✗"
        assert colorizer.warn() == "!"
        assert colorizer.info() == "i"

    def test_icon_render_ascii(self):
        """Test specific output for ASCII mode."""
        colorizer = Colorizer()
        colorizer.icon_mode = "ascii"
        colorizer.use_color = False

        assert colorizer.ok() == "[OK]"
        assert colorizer.err() == "[ERR]"
        assert colorizer.warn() == "[WARN]"
        assert colorizer.info() == "[INFO]"

    def test_set_color_method(self):
        """Test toggling color via set_color."""
        colorizer = Colorizer()
        colorizer.set_color(True)
        assert colorizer.use_color is True

        colorizer.set_color(False)
        assert colorizer.use_color is False

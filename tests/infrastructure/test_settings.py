import os
import tempfile
from pathlib import Path

from raztodo.infrastructure.settings import Settings


class TestSettings:

    def test_default_db_name(self):
        os.environ.pop("RAZTODO_DB", None)
        config = Settings()
        assert config.db_name == "tasks.db"

    def test_db_name_from_environment(self):
        os.environ["RAZTODO_DB"] = "custom.db"
        try:
            config = Settings()
            assert config.db_name == "custom.db"
        finally:
            os.environ.pop("RAZTODO_DB", None)

    def test_resolve_data_dir_default(self):
        os.environ.pop("XDG_DATA_HOME", None)
        config = Settings()
        expected = Path.home() / ".local/share/raztodo"
        assert config.data_dir == expected
        assert config.data_dir.exists()

    def test_resolve_data_dir_from_xdg(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["XDG_DATA_HOME"] = tmpdir
            try:
                config = Settings()
                expected = Path(tmpdir) / "raztodo"
                assert config.data_dir == expected
                assert config.data_dir.exists()
            finally:
                os.environ.pop("XDG_DATA_HOME", None)

    def test_db_path_relative(self):
        os.environ.pop("RAZTODO_DB", None)
        config = Settings()
        db_path = config.db_path
        assert db_path.is_absolute()
        assert db_path.name == "tasks.db"
        assert db_path.parent == config.data_dir

    def test_db_path_absolute(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            abs_db_path = Path(tmpdir) / "absolute.db"
            os.environ["RAZTODO_DB"] = str(abs_db_path)
            try:
                config = Settings()
                assert config.db_path == abs_db_path
            finally:
                os.environ.pop("RAZTODO_DB", None)

    def test_data_dir_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "raztodo" / "test"
            os.environ["XDG_DATA_HOME"] = str(data_dir.parent.parent)
            try:
                config = Settings()
                assert config.data_dir.exists()
            finally:
                os.environ.pop("XDG_DATA_HOME", None)

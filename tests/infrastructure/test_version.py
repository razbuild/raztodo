from importlib.metadata import PackageNotFoundError

import raztodo.infrastructure.version as version_module


def test_get_version_success(monkeypatch):
    monkeypatch.setattr(
        version_module,
        "version",
        lambda _: "1.2.3",
    )

    assert version_module.get_version() == "1.2.3"


def test_get_version_package_not_found(monkeypatch):
    def mock_version(_):
        raise PackageNotFoundError

    monkeypatch.setattr(
        version_module,
        "version",
        mock_version,
    )

    assert version_module.get_version() == "0.0.0-dev"

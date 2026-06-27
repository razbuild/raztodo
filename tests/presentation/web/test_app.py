from fastapi.testclient import TestClient

import raztodo.presentation.web.app as app_module


def test_index(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "render_index_html",
        lambda: "<html>OK</html>",
    )

    client = TestClient(app_module.app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "<html>OK</html>"

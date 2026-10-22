"""Testes unitários e de integração básicos para o app Akademus."""


def test_app_is_testing(app):
    """Garante que a aplicação inicializa no modo de teste."""
    assert app.config["TESTING"] is True


def test_healthcheck_endpoint(client):
    """Testa se o endpoint de healthcheck responde com status 200 e json esperado."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["app"] == "Akademus"

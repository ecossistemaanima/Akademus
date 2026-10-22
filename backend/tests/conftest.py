"""Fixtures globais do pytest para testes no Akademus."""

import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Cria e configura uma instância da aplicação para testes."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de testes HTTP do Flask."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Executor de comandos CLI do Flask."""
    return app.test_cli_runner()

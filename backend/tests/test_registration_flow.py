"""Testes automatizados para validação de política de senha, confirmação de senha e fluxo de pré-cadastro Google."""

import pytest
from app.models import University, User, Role
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Seed inicial para testes."""
    from app.seed import seed_database
    seed_database(app)


def test_password_policy_and_mismatch(client, seed_data):
    """Garante que senhas fracas ou que não coincidem são rejeitadas."""
    # 1. Senhas não coincidem
    payload_mismatch = {
        "name": "Aluno Teste",
        "email": "teste.mismatch@anima.edu.br",
        "password": "SenhaForte123!",
        "confirm_password": "OutraSenha123!",
        "university_id": 1,
        "role_type": "ALUNO",
        "ra": "RA12345"
    }
    res = client.post("/users/register", json=payload_mismatch)
    assert res.status_code == 400
    assert "não coincidem" in res.get_json()["error"]

    # 2. Senha sem caractere especial
    payload_weak = {
        "name": "Aluno Teste",
        "email": "teste.weak@anima.edu.br",
        "password": "SenhaSemEspecial123",
        "confirm_password": "SenhaSemEspecial123",
        "university_id": 1,
        "role_type": "ALUNO",
        "ra": "RA12345"
    }
    res2 = client.post("/users/register", json=payload_weak)
    assert res2.status_code == 400
    assert "caractere especial" in res2.get_json()["error"]


def test_university_is_required_in_registration(client, seed_data):
    """Cadastro sem universidade deve retornar erro 400."""
    payload = {
        "name": "Aluno Teste",
        "email": "teste.nouni@anima.edu.br",
        "password": "SenhaValida123!",
        "confirm_password": "SenhaValida123!",
        "role_type": "ALUNO",
        "ra": "RA12345"
    }
    res = client.post("/users/register", json=payload)
    assert res.status_code == 400
    assert "universidade" in res.get_json()["error"]


def test_google_first_time_login_workflow(client, seed_data):
    """Testa o fluxo onde um novo usuário Google complementa seu pré-cadastro com universidade e RA."""
    # 1. Simula sessão temporária criada pelo callback do Google
    with client.session_transaction() as sess:
        sess["pending_google_user"] = {
            "name": "Novo Estudante Google",
            "email": "novo.google@anima.edu.br",
            "sub": "google-sub-9999",
            "picture": "https://avatar.google.com/9999"
        }

    # 2. Usuário submete o formulário complementar de vínculo acadêmico
    res = client.post("/login/google/complete", data={
        "role_type": "ALUNO",
        "ra": "RA_GOOGLE_99",
        "university_id": 1
    })
    assert res.status_code == 200

    # 3. Verifica no banco que o usuário foi criado com status PENDING e vinculado à universidade
    with client.application.app_context():
        u = User.query.filter_by(email="novo.google@anima.edu.br").first()
        assert u is not None
        assert u.status == "PENDING"
        assert u.google_id == "google-sub-9999"
        assert u.ra == "RA_GOOGLE_99"
        assert len(u.universities) == 1
        assert u.universities[0].id == 1

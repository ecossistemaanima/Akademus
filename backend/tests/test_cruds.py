"""Testes de integração para os CRUDs de Universidades, Usuários, Moderação e Pré-Cadastro."""

import pytest
from app.models import University, User, Role
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Fixture que popula roles, universidades e admin para os testes."""
    from app.seed import seed_database
    seed_database(app)


def test_public_registration_pending_status(client, seed_data):
    """Garante que um estudante se cadastra com RA e status PENDING."""
    payload = {
        "name": "Aluno Novo",
        "email": "aluno.novo@anima.edu.br",
        "password": "SenhaSegura123!",
        "confirm_password": "SenhaSegura123!",
        "role_type": "ALUNO",
        "ra": "RA987654",
        "university_ids": [1, 2]
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["status"] == "PENDING"
    assert data["user"]["ra"] == "RA987654"
    assert "São Judas" in data["user"]["universities"]


def test_student_registration_requires_ra(client, seed_data):
    """Estudante tentando se cadastrar sem RA deve ser rejeitado (400)."""
    payload = {
        "name": "Aluno Sem RA",
        "email": "semra@anima.edu.br",
        "password": "SenhaSegura123!",
        "confirm_password": "SenhaSegura123!",
        "role_type": "ALUNO",
        "university_ids": [1],
        "ra": ""
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == 400
    assert "obrigatório" in response.get_json()["error"]


def test_admin_approval_workflow(client, seed_data):
    """Testa aprovação de cadastro pendente pelo Administrador."""
    # 1. Pré-cadastro do usuário
    reg = client.post("/users/register", json={
        "name": "Candidato",
        "email": "candidato@anima.edu.br",
        "password": "SenhaSegura123!",
        "confirm_password": "SenhaSegura123!",
        "university_ids": [1],
        "role_type": "PROFESSOR",
        "ra": ""
    })
    assert reg.status_code == 201
    user_id = reg.get_json()["user"]["id"]

    # 2. Simula sessão como Admin
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # 3. Aprova o cadastro
    resp = client.post(f"/users/api/{user_id}/status", json={"status": "APPROVED"})
    assert resp.status_code == 200
    assert resp.get_json()["user"]["status"] == "APPROVED"


def test_non_admin_cannot_access_crud(client, seed_data):
    """Usuário não administrador recebe 403 ao tentar criar ou listar universidades administrativamente."""
    # Simula sessão de um aluno
    with client.session_transaction() as sess:
        sess["user"] = {"email": "aluno@anima.edu.br", "name": "Aluno Comum"}

    resp = client.post("/universities/api", json={
        "code": "NOVA_FACULDADE",
        "name": "Nova Faculdade",
        "short_name": "Nova"
    })
    assert resp.status_code == 403

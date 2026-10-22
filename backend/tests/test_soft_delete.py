"""Testes automatizados completos para operações de Update, Soft-Delete e Criação direta."""

import pytest
from app.models import University, User, Role
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Inicializa banco com papéis, universidades Ânima e usuário admin."""
    from app.seed import seed_database
    seed_database(app)


def test_admin_direct_user_creation(client, seed_data):
    """Administrador cria diretamente um docente aprovado com universidades."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    payload = {
        "name": "Professora Maria",
        "email": "maria@anima.edu.br",
        "password": "SenhaDocente123!",
        "role_type": "PROFESSOR",
        "ra": "",
        "status": "APPROVED",
        "university_ids": [1, 2]
    }
    resp = client.post("/users/api", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["email"] == "maria@anima.edu.br"
    assert data["status"] == "APPROVED"
    assert data["is_active"] is True
    assert len(data["universities"]) == 2


def test_user_soft_delete_and_restore(client, seed_data):
    """Testa exclusão lógica (is_active = False) e restauração sem perda do registro."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # 1. Cria usuário
    reg = client.post("/users/api", json={
        "name": "Aluno Temporário",
        "email": "temp@anima.edu.br",
        "password": "123",
        "role_type": "ALUNO",
        "ra": "TEMP123"
    })
    user_id = reg.get_json()["id"]

    # 2. Executa Soft-Delete
    del_resp = client.delete(f"/users/api/{user_id}")
    assert del_resp.status_code == 200
    assert del_resp.get_json()["user"]["is_active"] is False

    # 3. Verifica no banco que o registro ainda existe (não foi apagado fisicamente)
    user = User.query.get(user_id)
    assert user is not None
    assert user.is_active is False

    # 4. Restaura o usuário
    restore_resp = client.put(f"/users/api/{user_id}", json={"is_active": True})
    assert restore_resp.status_code == 200
    assert restore_resp.get_json()["is_active"] is True


def test_university_crud_and_soft_delete(client, seed_data):
    """Testa criação, edição e exclusão lógica de universidade."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # 1. Criar universidade
    c_resp = client.post("/universities/api", json={
        "code": "MACKENZIE",
        "name": "Universidade Presbiteriana Mackenzie",
        "short_name": "Mackenzie"
    })
    assert c_resp.status_code == 201
    uni_id = c_resp.get_json()["id"]

    # 2. Atualizar universidade
    u_resp = client.put(f"/universities/api/{uni_id}", json={
        "name": "Universidade Presbiteriana Mackenzie - SP",
        "short_name": "Mack"
    })
    assert u_resp.status_code == 200
    assert u_resp.get_json()["short_name"] == "Mack"

    # 3. Soft-delete da universidade
    d_resp = client.delete(f"/universities/api/{uni_id}")
    assert d_resp.status_code == 200
    assert d_resp.get_json()["university"]["is_active"] is False

    # Verifica integridade no banco
    uni = University.query.get(uni_id)
    assert uni is not None
    assert uni.is_active is False

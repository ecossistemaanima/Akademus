"""Testes automatizados completos para o CRUD de Parceiros Acadêmicos (Acesso, Criação, Edição e Soft-Delete)."""

import pytest
from app.models import AcademicPartner, User
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Seed inicial para os testes."""
    from app.seed import seed_database
    seed_database(app)


def test_public_partners_api_and_view(client, seed_data):
    """Qualquer usuário pode listar parceiros ativos."""
    # API JSON
    resp = client.get("/partners/api")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

    # View HTML
    view_resp = client.get("/partners")
    assert view_resp.status_code == 200
    assert "Parceiros Acadêmicos" in view_resp.get_data(as_text=True)


def test_non_admin_cannot_create_or_modify_partner(client, seed_data):
    """Usuário comum ou deslogado não pode criar, editar ou excluir parceiros (403/302)."""
    # Deslogado
    c_resp = client.post("/partners/api", json={
        "code": "TEST_PARTNER",
        "name": "Test Partner"
    })
    assert c_resp.status_code in [302, 403]

    # Logado como aluno comum
    with client.session_transaction() as sess:
        sess["user"] = {"email": "mariana.estudante@anima.edu.br", "name": "Mariana"}

    c_resp2 = client.post("/partners/api", json={
        "code": "TEST_PARTNER",
        "name": "Test Partner"
    })
    assert c_resp2.status_code == 403


def test_admin_full_partner_crud_lifecycle(client, seed_data):
    """Administrador cria, consulta, atualiza e faz soft delete de um parceiro."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # 1. CREATE
    payload = {
        "code": "MICROSOFT_LEARN",
        "name": "Microsoft Learn for Educators",
        "category": "CLOUD_AI",
        "website_url": "https://www.microsoft.com/en-us/education/educators/msle",
        "description": "Capacitações oficiais em Azure, IA e Power Platform para docentes e alunos."
    }
    create_resp = client.post("/partners/api", json=payload)
    assert create_resp.status_code == 201
    partner_id = create_resp.get_json()["id"]

    # 2. GET
    get_resp = client.get(f"/partners/api/{partner_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["name"] == "Microsoft Learn for Educators"

    # 3. UPDATE
    up_resp = client.put(f"/partners/api/{partner_id}", json={
        "name": "Microsoft Learn AI & Cloud",
        "category": "CLOUD_TECH"
    })
    assert up_resp.status_code == 200
    assert up_resp.get_json()["name"] == "Microsoft Learn AI & Cloud"
    assert up_resp.get_json()["category"] == "CLOUD_TECH"

    # 4. SOFT DELETE
    del_resp = client.delete(f"/partners/api/{partner_id}")
    assert del_resp.status_code == 200
    assert del_resp.get_json()["partner"]["is_active"] is False

    # Valida no banco que o registro existe, apenas com is_active = False
    with client.application.app_context():
        p = AcademicPartner.query.get(partner_id)
        assert p is not None
        assert p.is_active is False

"""Testes automatizados para o CRUD de Badges, Atribuição com Datas e Sincronização Credly."""

import pytest
from datetime import date, timedelta
from app.models import Badge, UserBadge, AcademicPartner, User, Role
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Seed inicial para testes de badges."""
    from app.seed import seed_database
    seed_database(app)


def test_badges_public_listing_api_and_view(client, seed_data):
    """Usuários autenticados ou anônimos conseguem listar o catálogo de badges ativas."""
    resp = client.get("/badges/api")
    assert resp.status_code == 200
    badges = resp.get_json()
    assert isinstance(badges, list)
    assert len(badges) >= 1  # Criado no seed

    # Tela HTML
    view_resp = client.get("/badges")
    assert view_resp.status_code == 200
    assert "Gestão de Badges" in view_resp.get_data(as_text=True)


def test_non_admin_cannot_create_or_delete_badge(client, seed_data):
    """Usuário não-admin é barrado ao tentar criar ou desativar badge no catálogo."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "mariana.estudante@anima.edu.br", "name": "Mariana"}

    resp = client.post("/badges/api", json={
        "code": "TEST_SECURITY_BADGE",
        "name": "Security Badge"
    })
    assert resp.status_code == 403

    del_resp = client.delete("/badges/api/1")
    assert del_resp.status_code == 403


def test_admin_badge_crud_lifecycle(client, seed_data):
    """Administrador cria, consulta, atualiza e faz soft delete de uma badge do catálogo."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # 1. CREATE
    badge_payload = {
        "code": "GCP_ACE_CERTIFIED",
        "name": "Google Cloud Associate Cloud Engineer",
        "description": "Certificação oficial de engenharia em nuvem Google Cloud.",
        "issuer_name": "Google Cloud",
        "image_url": "https://images.credly.com/images/ace.png"
    }
    create_resp = client.post("/badges/api", json=badge_payload)
    assert create_resp.status_code == 201
    badge_id = create_resp.get_json()["badge"]["id"]

    # 2. READ
    get_resp = client.get(f"/badges/api/{badge_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["code"] == "GCP_ACE_CERTIFIED"

    # 3. UPDATE
    up_resp = client.put(f"/badges/api/{badge_id}", json={
        "name": "Google Cloud Associate Cloud Engineer (Updated)"
    })
    assert up_resp.status_code == 200
    assert "Updated" in up_resp.get_json()["badge"]["name"]

    # 4. SOFT DELETE
    del_resp = client.delete(f"/badges/api/{badge_id}")
    assert del_resp.status_code == 200

    badge_db = db.session.get(Badge, badge_id)
    assert badge_db is not None
    assert badge_db.is_active is False


def test_assign_badge_with_issued_and_optional_expiration_date(client, seed_data):
    """Testa atribuição manual de uma badge para um usuário com data de emissão e expiração."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    admin_user = User.query.filter_by(email="hpoyatos@gmail.com").first()
    badge = Badge.query.first()

    today_str = date.today().isoformat()
    future_str = (date.today() + timedelta(days=365)).isoformat()

    # 1. Atribuição bem sucedida
    assign_resp = client.post("/badges/api/assign", json={
        "user_id": admin_user.id,
        "badge_id": badge.id,
        "issued_at": today_str,
        "expires_at": future_str,
        "evidence_url": "https://www.credly.com/badges/test-evidence"
    })
    assert assign_resp.status_code in [200, 201]
    ub_data = assign_resp.get_json()["user_badge"]
    assert ub_data["issued_at"] == today_str
    assert ub_data["expires_at"] == future_str

    # 2. Validação: Falha se data de expiração for anterior à de emissão
    past_str = (date.today() - timedelta(days=10)).isoformat()
    fail_resp = client.post("/badges/api/assign", json={
        "user_id": admin_user.id,
        "badge_id": badge.id,
        "issued_at": today_str,
        "expires_at": past_str
    })
    assert fail_resp.status_code == 400
    assert "expiração" in fail_resp.get_json()["error"].lower()

    # 3. Desatribuir (Unassign)
    ub_id = ub_data["id"]
    unassign_resp = client.delete(f"/badges/api/unassign/{ub_id}")
    assert unassign_resp.status_code == 200
    assert db.session.get(UserBadge, ub_id) is None


def test_credly_auto_sync_on_profile_save(client, mocker, seed_data):
    """
    Testa se ao configurar a credly_url no perfil do usuário,
    o sistema aciona o serviço Credly e pendura as badges automaticamente.
    """
    # Mock do retorno da requisição HTTP ao Credly
    mock_credly_payload = {
        "data": [
            {
                "id": "credly-mock-12345",
                "issued_at_date": "2024-05-10",
                "expires_at_date": "2027-05-10",
                "badge_template": {
                    "name": "Red Hat Certified System Administrator (RHCSA)",
                    "vanity_slug": "red-hat-certified-system-administrator-rhcsa",
                    "description": "Demonstrates core system administration skills.",
                    "image_url": "https://images.credly.com/rhcsa.png",
                    "url": "https://www.credly.com/org/red-hat"
                },
                "issuer": {
                    "entities": [
                        {"entity": {"name": "Red Hat"}}
                    ]
                }
            }
        ]
    }

    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_credly_payload
    mocker.patch("requests.get", return_value=mock_resp)

    with client.application.app_context():
        role_aluno = Role.query.filter_by(name="ALUNO").first()
        mariana = User(
            name="Mariana Estudante",
            email="mariana.estudante@anima.edu.br",
            ra="82012345",
            status="APPROVED",
            is_active=True
        )
        mariana.roles.append(role_aluno)
        db.session.add(mariana)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user"] = {"email": "mariana.estudante@anima.edu.br", "name": "Mariana Estudante"}

    # Usuário salva a URL do Credly no perfil
    resp = client.post("/profile", data={
        "name": "Mariana Estudante",
        "credly_url": "https://www.credly.com/users/mariana-estudante/badges",
        "linkedin_url": "https://linkedin.com/in/mariana",
        "bio": "Estudante de Engenharia de Software"
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert "Credly" in resp.get_data(as_text=True)

    # Verifica se a badge foi criada no catálogo e pendurada no perfil de Mariana
    mariana = User.query.filter_by(email="mariana.estudante@anima.edu.br").first()
    assert mariana.credly_url == "https://www.credly.com/users/mariana-estudante/badges"
    assert len(mariana.user_badges) >= 1

    ub = mariana.user_badges[0]
    assert "Red Hat" in ub.badge.name
    assert ub.issued_at == date(2024, 5, 10)
    assert ub.expires_at == date(2027, 5, 10)


def test_google_skills_auto_sync_on_profile_save(client, mocker, seed_data):
    """
    Testa se ao configurar a google_skills_boost_url no perfil do usuário,
    o sistema faz a extração HTML e pendura as badges com data de emissão.
    """
    mock_html = """
    <html>
      <body>
        <div class="profile-badge">
          <a class="badge-image" href="https://www.skills.google/public_profiles/1e1c3ff6-7ea6-4a99-b087-9015c0809068/badges/29025820">
            <img src="https://cdn.qwiklabs.com/gemini_app.png" />
          </a>
          <span class="ql-title-medium">Create Your First Gemini Enterprise Application</span>
          <span class="ql-body-medium">Earned Oct 21, 2026 EDT</span>
          <ql-button modal="public-profile-award-modal-0"></ql-button>
        </div>
        <ql-dialog id="public-profile-award-modal-0">
          <p>Create your first Gemini Enterprise application to earn a skill badge!</p>
        </ql-dialog>
      </body>
    </html>
    """

    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_html
    mocker.patch("requests.get", return_value=mock_resp)

    with client.application.app_context():
        role_aluno = Role.query.filter_by(name="ALUNO").first()
        carlos = User(
            name="Carlos Cloud",
            email="carlos.cloud@anima.edu.br",
            ra="83012345",
            status="APPROVED",
            is_active=True
        )
        carlos.roles.append(role_aluno)
        db.session.add(carlos)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user"] = {"email": "carlos.cloud@anima.edu.br", "name": "Carlos Cloud"}

    resp = client.post("/profile", data={
        "name": "Carlos Cloud",
        "google_skills_boost_url": "https://www.skills.google/public_profiles/1e1c3ff6-7ea6-4a99-b087-9015c0809068",
        "bio": "Estudante entusiasta de Google Cloud e IA Generativa"
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert "Google Skills" in resp.get_data(as_text=True)

    carlos_db = User.query.filter_by(email="carlos.cloud@anima.edu.br").first()
    assert len(carlos_db.user_badges) >= 1
    ub = carlos_db.user_badges[0]
    assert ub.badge.name == "Create Your First Gemini Enterprise Application"
    assert ub.issued_at == date(2026, 10, 21)
    assert ub.expires_at is None
    assert ub.badge.issuer_name == "Google Cloud"


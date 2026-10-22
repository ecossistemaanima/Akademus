"""Testes automatizados para Parceiros Acadêmicos, Edição de Perfil e Controle de Visibilidade de Credly/LinkedIn."""

import pytest
from app.models import University, User, Role, AcademicPartner
from app.extensions import db


@pytest.fixture
def seed_data(app):
    """Seed inicial para os testes."""
    from app.seed import seed_database
    seed_database(app)


def test_academic_partners_creation(app):
    """Valida a criação e recuperação de parceiros acadêmicos (Google Cloud, Red Hat, AWS, Cisco, etc)."""
    with app.app_context():
        p = AcademicPartner(
            code="GOOGLE_CLOUD",
            name="Google Cloud",
            category="CLOUD_AI",
            website_url="https://cloud.google.com/edu"
        )
        db.session.add(p)
        db.session.commit()

        partner = AcademicPartner.query.filter_by(code="GOOGLE_CLOUD").first()
        assert partner is not None
        assert partner.name == "Google Cloud"
        assert partner.category == "CLOUD_AI"


def test_user_profile_edit_and_email_immutable(client, seed_data):
    """Garante que o usuário pode atualizar bio, avatar, credly_url e visibilidade, mas seu e-mail não muda."""
    with client.session_transaction() as sess:
        sess["user"] = {"email": "hpoyatos@gmail.com", "name": "Prof. Henrique Poyatos"}

    # Atualiza o perfil
    resp = client.post("/profile", data={
        "name": "Prof. Henrique Poyatos PhD",
        "google_picture": "https://images.credly.com/avatar_atualizado.png",
        "bio": "Professor e Coordenador de Tecnologia com foco em Cloud e IA.",
        "credly_url": "https://www.credly.com/users/hpoyatos/badges/credly",
        "linkedin_url": "https://www.linkedin.com/in/hpoyatos",
        "google_skills_boost_url": "https://www.cloudskillsboost.google/public_profiles/hpoyatos",
        "is_profile_public": "true"
    }, follow_redirects=True)

    assert resp.status_code == 200

    # Verifica no banco de dados
    with client.application.app_context():
        user = User.query.filter_by(email="hpoyatos@gmail.com").first()
        assert user.name == "Prof. Henrique Poyatos PhD"
        assert user.email == "hpoyatos@gmail.com"  # e-mail intacto
        assert user.credly_url == "https://www.credly.com/users/hpoyatos/badges/credly"
        assert user.is_profile_public is True


def test_privacy_visibility_control(app):
    """
    Testa regra de privacidade:
    - Se is_profile_public for False, outro aluno NÃO vê o Credly/LinkedIn.
    - O próprio usuário, Administradores e Professores SEMPRE conseguem ver.
    """
    with app.app_context():
        # Cria aluno com perfil privado
        aluno_privado = User(
            name="Estudante Discreto",
            email="discreto@anima.edu.br",
            ra="998877",
            status="APPROVED",
            credly_url="https://www.credly.com/users/discreto/badges",
            linkedin_url="https://www.linkedin.com/in/discreto",
            is_profile_public=False
        )
        # Outro aluno comum
        outro_aluno = User(name="Outro Aluno", email="outro@anima.edu.br", status="APPROVED")
        # Professor
        prof = User(name="Professor", email="prof@anima.edu.br", status="APPROVED")
        role_prof = Role(name="PROFESSOR")
        prof.roles.append(role_prof)

        db.session.add_all([aluno_privado, outro_aluno, prof, role_prof])
        db.session.commit()

        # 1. Outro aluno tentando ver os dados do aluno privado -> deve vir None
        dict_para_aluno = aluno_privado.to_dict(viewer=outro_aluno)
        assert dict_para_aluno["credly_url"] is None
        assert dict_para_aluno["linkedin_url"] is None

        # 2. O próprio aluno visualizando seu perfil -> vê os dados
        dict_proprio = aluno_privado.to_dict(viewer=aluno_privado)
        assert dict_proprio["credly_url"] == "https://www.credly.com/users/discreto/badges"

        # 3. O Professor visualizando -> SEMPRE vê, mesmo privado
        dict_para_prof = aluno_privado.to_dict(viewer=prof)
        assert dict_para_prof["credly_url"] == "https://www.credly.com/users/discreto/badges"
        assert dict_para_prof["linkedin_url"] == "https://www.linkedin.com/in/discreto"

"""Testes unitários e de integração para Universidades, Usuários, Validações e Permissões."""

import pytest
from app.models import University, User, Role
from app.extensions import db


def test_university_model_constraints(app):
    """Testa criação e restrição de unicidade em University.code."""
    with app.app_context():
        u1 = University(code="USJT", name="Universidade São Judas Tadeu", short_name="São Judas")
        db.session.add(u1)
        db.session.commit()

        assert u1.id is not None
        assert u1.short_name == "São Judas"

        # Tenta duplicar o código
        with pytest.raises(Exception):
            u2 = University(code="USJT", name="Duplicada", short_name="Duplicada")
            db.session.add(u2)
            db.session.commit()
        db.session.rollback()


def test_user_creation_and_ra_rule(app):
    """Testa regra de RA: aluno com RA obrigatório, professor sem RA."""
    with app.app_context():
        # Cria roles
        role_aluno = Role(name="ALUNO", description="Estudante")
        role_prof = Role(name="PROFESSOR", description="Docente")
        db.session.add_all([role_aluno, role_prof])
        db.session.commit()

        # Aluno com RA
        aluno = User(name="Estudante Teste", email="aluno@anima.edu.br", ra="12345678", status="PENDING")
        aluno.roles.append(role_aluno)
        db.session.add(aluno)

        # Professor sem RA
        prof = User(name="Prof. Teste", email="prof@anima.edu.br", ra=None, status="APPROVED")
        prof.roles.append(role_prof)
        db.session.add(prof)

        db.session.commit()

        assert aluno.ra == "12345678"
        assert prof.ra is None
        assert aluno.has_role("ALUNO")
        assert prof.has_role("PROFESSOR")


def test_user_multi_universities_association(app):
    """Testa associação N:N entre um usuário e múltiplas universidades."""
    with app.app_context():
        u_usjt = University(code="USJT", name="São Judas", short_name="USJT")
        u_uam = University(code="UAM", name="Anhembi Morumbi", short_name="UAM")
        db.session.add_all([u_usjt, u_uam])
        db.session.commit()

        hpoyatos = User(name="Henrique Poyatos", email="hpoyatos@gmail.com", status="APPROVED")
        hpoyatos.universities.extend([u_usjt, u_uam])
        db.session.add(hpoyatos)
        db.session.commit()

        loaded_user = User.query.filter_by(email="hpoyatos@gmail.com").first()
        assert len(loaded_user.universities) == 2
        codes = [u.code for u in loaded_user.universities]
        assert "USJT" in codes
        assert "UAM" in codes


def test_seed_creates_anima_universities_and_admin(app):
    """Garante que o seed cria as 18 instituições da Ânima e o usuário mestre hpoyatos@gmail.com."""
    from app.seed import seed_database
    seed_database(app)

    with app.app_context():
        total_unis = University.query.count()
        assert total_unis >= 18

        admin = User.query.filter_by(email="hpoyatos@gmail.com").first()
        assert admin is not None
        assert admin.is_admin is True
        assert admin.status == "APPROVED"
        assert len(admin.universities) == total_unis

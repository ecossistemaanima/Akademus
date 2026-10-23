"""Módulo de autenticação e rotas de login (Tradicional e Google OAuth)."""

import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint("auth", __name__)
oauth = OAuth()


def configure_oauth(app):
    """Registra e configura o provedor Google OAuth no Flask."""
    oauth.init_app(app)

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if google_client_id and google_client_secret:
        oauth.register(
            name="google",
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Tela de login."""
    from app.models import University, User

    unis = University.query.filter_by(is_active=True).order_by(University.name.asc()).all()

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return render_template(
                "login.html",
                error="E-mail ou senha inválidos.",
                universities=unis
            )

        if not user.is_active:
            return render_template(
                "login.html",
                error="Este cadastro foi desativado pela moderação.",
                universities=unis
            )

        if user.status != "APPROVED":
            return render_template(
                "login.html",
                error=f"Seu cadastro está com status '{user.status}'. Aguarde a aprovação do Administrador.",
                universities=unis
            )

        session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "picture": user.google_picture,
            "is_admin": user.is_admin,
            "roles": [r.name for r in user.roles]
        }

        # Sincroniza usuário e credenciais no Stout Chat silenciosamente
        try:
            from app.services.stout_service import sync_user_to_stout
            sync_user_to_stout(email=user.email, password=password, username=user.name)
        except Exception:
            pass

        return redirect(url_for("index"))

    return render_template("login.html", universities=unis)


@auth_bp.route("/login/google")
def login_google():
    """Inicia o fluxo OAuth com o Google."""
    google = oauth.create_client("google")
    if not google:
        return render_template(
            "login.html",
            info="Google OAuth precisa de GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET configurados no .env."
        )

    # Constrói redirect_uri público com HTTPS forçado para atender ao Google OAuth
    base_host = os.getenv("APP_HOST", request.host)
    redirect_uri = f"https://{base_host}/login/callback"
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/callback")
def google_callback():
    """Recebe o retorno do Google OAuth com o perfil do usuário."""
    from app.models import User, University
    from app.extensions import db

    google = oauth.create_client("google")
    if not google:
        return redirect(url_for("auth.login"))

    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        return render_template("login.html", error="Falha ao obter dados da conta Google.")

    email = user_info.get("email").lower()
    user = User.query.filter_by(email=email).first()

    # Se o usuário NÃO existe no banco de dados, guarda dados temporários na sessão e solicita dados acadêmicos
    if not user:
        session["pending_google_user"] = {
            "name": user_info.get("name", "Usuário"),
            "email": email,
            "sub": user_info.get("sub"),
            "picture": user_info.get("picture"),
        }
        unis = University.query.filter_by(is_active=True).order_by(University.name.asc()).all()
        return render_template(
            "google_register.html",
            pending_user=session["pending_google_user"],
            universities=unis
        )

    # Se existe mas foi desativado
    if not user.is_active:
        return render_template("login.html", error="Seu cadastro foi desativado pela moderação.")

    # Se existir mas estiver PENDING ou REJECTED
    if user.status != "APPROVED":
        return render_template(
            "login.html",
            error=f"Seu cadastro está com status '{user.status}'. Aguarde a liberação do Administrador."
        )

    # Atualiza foto e sub caso não estejam salvos
    if not user.google_id:
        user.google_id = user_info.get("sub")
        user.google_picture = user_info.get("picture")
        db.session.commit()

    session["user"] = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "picture": user.google_picture,
        "is_admin": user.is_admin,
        "roles": [r.name for r in user.roles]
    }
    return redirect(url_for("index"))


@auth_bp.route("/login/google/complete", methods=["POST"])
def complete_google_registration():
    """Recebe universidade, perfil e RA para novos cadastros via Google."""
    from app.models import User, University, Role
    from app.extensions import db

    pending = session.get("pending_google_user")
    if not pending:
        return redirect(url_for("auth.login"))

    role_type = (request.form.get("role_type") or "ALUNO").strip().upper()
    ra = (request.form.get("ra") or "").strip()
    uni_id = request.form.get("university_id")

    unis = University.query.filter_by(is_active=True).order_by(University.name.asc()).all()

    if role_type == "ALUNO" and not ra:
        return render_template("google_register.html", pending_user=pending, universities=unis, error="RA é obrigatório para estudantes.")

    if not uni_id:
        return render_template("google_register.html", pending_user=pending, universities=unis, error="Selecione sua universidade.")

    uni = University.query.get(int(uni_id))
    if not uni:
        return render_template("google_register.html", pending_user=pending, universities=unis, error="Universidade inválida.")

    # Cria o usuário com status PENDING
    user = User(
        name=pending["name"],
        email=pending["email"],
        google_id=pending["sub"],
        google_picture=pending["picture"],
        ra=ra if role_type == "ALUNO" else None,
        status="PENDING",
        is_active=True
    )

    role = Role.query.filter_by(name=role_type).first()
    if role:
        user.roles.append(role)
    user.universities.append(uni)

    db.session.add(user)
    db.session.commit()

    # Limpa sessão pendente
    session.pop("pending_google_user", None)

    return render_template(
        "login.html",
        info="Solicitação de pré-cadastro Google enviada com sucesso! Aguarde a aprovação do Administrador.",
        universities=unis
    )


@auth_bp.route("/logout")
def logout():
    """Encerra a sessão."""
    session.pop("user", None)
    return redirect(url_for("auth.login"))

"""CRUD de Usuários, Moderação de Cadastros e Autocadastro de Usuário."""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import User, University, Role
from app.extensions import db
from app.routes.universities import admin_required

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/profile", methods=["GET", "POST"])
def edit_my_profile():
    """Tela de edição do próprio perfil pelo usuário autenticado."""
    user_data = session.get("user")
    if not user_data:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=user_data.get("email")).first_or_404()

    success_msg = None
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if name:
            user.name = name
            user_data["name"] = name

        user.google_picture = request.form.get("google_picture") or None
        user_data["picture"] = user.google_picture

        new_credly_url = (request.form.get("credly_url") or "").strip() or None
        user.credly_url = new_credly_url
        user.linkedin_url = (request.form.get("linkedin_url") or "").strip() or None
        
        new_skills_url = (request.form.get("google_skills_boost_url") or "").strip() or None
        user.google_skills_boost_url = new_skills_url
        user.is_profile_public = (request.form.get("is_profile_public") == "true")

        # Dispara sincronização automática com Credly se informado
        sync_messages = []
        if new_credly_url:
            from app.services.credly_service import sync_user_credly_badges
            sync_res = sync_user_credly_badges(user, new_credly_url)
            if sync_res.get("status") == "success":
                sync_messages.append(f"{sync_res.get('imported', 0)} insígnias do Credly")
            else:
                sync_messages.append(f"Aviso Credly: {sync_res.get('message')}")

        # Dispara sincronização automática com Google Skills Boost se informado
        if new_skills_url:
            from app.services.google_skills_service import sync_user_google_skills_badges
            skills_res = sync_user_google_skills_badges(user, new_skills_url)
            if skills_res.get("status") == "success":
                sync_messages.append(f"{skills_res.get('imported', 0)} insígnias do Google Skills")
            else:
                sync_messages.append(f"Aviso Google Skills: {skills_res.get('message')}")

        db.session.commit()
        session["user"] = user_data
        
        sync_feedback = f" (Sincronizado: {', '.join(sync_messages)})" if sync_messages else ""
        success_msg = f"Perfil atualizado com sucesso!{sync_feedback}"

    return render_template("profile.html", user=user, success=success_msg)


@users_bp.route("/register", methods=["POST"])
def register_user():
    """Endpoint público para pré-cadastro de estudantes e docentes."""
    from app.utils import validate_password_policy

    data = request.get_json() or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    role_type = (data.get("role_type") or "ALUNO").strip().upper()
    ra = (data.get("ra") or "").strip()
    university_ids = data.get("university_ids") or data.get("university_id") or []

    if not name or not email or not password:
        return jsonify({"error": "Nome, e-mail e senha são obrigatórios."}), 400

    # Confirmação de senha
    if password != confirm_password:
        return jsonify({"error": "A senha e a confirmação de senha não coincidem."}), 400

    # Política de senha
    is_valid, msg = validate_password_policy(password)
    if not is_valid:
        return jsonify({"error": msg}), 400

    # Validação do RA: Aluno tem RA obrigatório; Professor não tem
    if role_type == "ALUNO" and not ra:
        return jsonify({"error": "O campo Registro de Aluno (RA) é obrigatório para estudantes."}), 400

    if not university_ids:
        return jsonify({"error": "Selecione a universidade / instituição de ensino."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "E-mail já cadastrado no sistema."}), 409

    # Cria usuário com status PENDING para aprovação do administrador
    user = User(
        name=name,
        email=email,
        ra=ra if role_type == "ALUNO" else None,
        status="PENDING",
        is_active=True
    )
    user.set_password(password)

    # Associa papel (Role)
    role = Role.query.filter_by(name=role_type).first()
    if role:
        user.roles.append(role)

    # Associa Universidades
    if university_ids:
        if isinstance(university_ids, str):
            university_ids = [int(x) for x in university_ids.split(",") if x.isdigit()]
        unis = University.query.filter(University.id.in_(university_ids)).all()
        user.universities = unis

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Cadastro realizado com sucesso! Aguarde a aprovação do Administrador.",
        "user": user.to_dict()
    }), 201


@users_bp.route("/", methods=["GET"])
@admin_required
def list_users_view():
    """Tela administrativa de listagem e moderação de usuários com suporte a filtros."""
    status_filter = request.args.get("status")
    query = User.query
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    
    users = query.order_by(User.created_at.desc()).all()
    unis = University.query.filter_by(is_active=True).order_by(University.short_name.asc()).all()
    roles = Role.query.all()
    
    # Contadores rápidos para as abas de filtro
    counts = {
        "ALL": User.query.count(),
        "PENDING": User.query.filter_by(status="PENDING").count(),
        "APPROVED": User.query.filter_by(status="APPROVED").count(),
        "REJECTED": User.query.filter_by(status="REJECTED").count(),
    }
    
    return render_template(
        "users.html",
        users=users,
        universities=unis,
        roles=roles,
        current_status=status_filter.upper() if status_filter else "ALL",
        counts=counts,
        current_user=session.get("user")
    )


@users_bp.route("/api", methods=["GET"])
@admin_required
def list_users_api():
    """API de listagem de usuários."""
    status_filter = request.args.get("status")
    query = User.query
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.route("/api", methods=["POST"])
@admin_required
def create_user_admin():
    """Criação direta de usuário pelo Administrador (já com status APPROVED ou o que desejar)."""
    data = request.get_json() or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or "Akademus@2026"
    role_type = (data.get("role_type") or "ALUNO").strip().upper()
    ra = (data.get("ra") or "").strip()
    status = (data.get("status") or "APPROVED").strip().upper()
    university_ids = data.get("university_ids") or []

    if not name or not email:
        return jsonify({"error": "Nome e e-mail são obrigatórios."}), 400

    if role_type == "ALUNO" and not ra:
        return jsonify({"error": "RA é obrigatório para perfil Aluno."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "E-mail já cadastrado."}), 409

    user = User(
        name=name,
        email=email,
        ra=ra if role_type == "ALUNO" else None,
        status=status,
        is_active=True
    )
    user.set_password(password)

    role = Role.query.filter_by(name=role_type).first()
    if role:
        user.roles.append(role)

    if university_ids:
        if isinstance(university_ids, str):
            university_ids = [int(x) for x in university_ids.split(",") if x.isdigit()]
        unis = University.query.filter(University.id.in_(university_ids)).all()
        user.universities = unis

    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@users_bp.route("/api/<int:user_id>", methods=["GET"])
@admin_required
def get_user_api(user_id):
    """Retorna detalhes de um usuário."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@users_bp.route("/api/<int:user_id>", methods=["PUT", "POST"])
@admin_required
def update_user_api(user_id):
    """Atualização cadastral de usuário pelo Administrador."""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or request.form

    if "name" in data and data["name"].strip():
        user.name = data["name"].strip()
    if "email" in data and data["email"].strip():
        new_email = data["email"].strip().lower()
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "E-mail já está em uso por outro usuário."}), 409
        user.email = new_email
    if "ra" in data:
        user.ra = data["ra"].strip() if data["ra"] else None
    if "status" in data and data["status"].strip().upper() in ["PENDING", "APPROVED", "REJECTED"]:
        user.status = data["status"].strip().upper()
    if "is_active" in data:
        val = data["is_active"]
        user.is_active = (val is True or val == "true" or val == "1" or val == 1)

    # Atualiza papéis se informado
    if "role_type" in data:
        role = Role.query.filter_by(name=data["role_type"].strip().upper()).first()
        if role:
            user.roles = [role]

    # Atualiza universidades se informado
    if "university_ids" in data:
        u_ids = data["university_ids"]
        if isinstance(u_ids, str):
            u_ids = [int(x) for x in u_ids.split(",") if x.isdigit()]
        user.universities = University.query.filter(University.id.in_(u_ids)).all()

    db.session.commit()
    return jsonify(user.to_dict()), 200


@users_bp.route("/api/<int:user_id>/status", methods=["PATCH", "POST"])
@admin_required
def update_user_status(user_id):
    """Aprova (APPROVED) ou rejeita (REJECTED) um pré-cadastro."""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or request.form
    new_status = (data.get("status") or "").upper()

    if new_status not in ["APPROVED", "REJECTED", "PENDING"]:
        return jsonify({"error": "Status inválido. Use APPROVED, REJECTED ou PENDING."}), 400

    user.status = new_status
    db.session.commit()
    return jsonify({"message": f"Usuário {user.email} atualizado para {new_status}.", "user": user.to_dict()}), 200


@users_bp.route("/api/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Exclusão LÓGICA (Soft Delete): Desativa o usuário (is_active = False) sem apagar dados históricos."""
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({
        "message": f"Usuário {user.email} foi desativado com sucesso (exclusão lógica).",
        "user": user.to_dict()
    }), 200

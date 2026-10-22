"""CRUD de Badges / Insígnias Digitais e Atribuição a Usuários."""

from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import Badge, UserBadge, AcademicPartner, User
from app.extensions import db
from app.routes.universities import admin_required
from app.services.credly_service import sync_user_credly_badges

badges_bp = Blueprint("badges", __name__, url_prefix="/badges")


@badges_bp.route("/api", methods=["GET"], strict_slashes=False)
def list_badges_api():
    """Retorna lista do catálogo de badges em formato JSON."""
    active_only = request.args.get("active_only", "true").lower() == "true"
    query = Badge.query
    if active_only:
        query = query.filter_by(is_active=True)
    badges = query.order_by(Badge.name.asc()).all()
    return jsonify([b.to_dict() for b in badges]), 200


@badges_bp.route("/", methods=["GET"], strict_slashes=False)
def index_view():
    """Interface de gestão do catálogo de Badges e de atribuição a usuários."""
    user_data = session.get("user")
    is_admin = False
    current_user_obj = None
    if user_data:
        current_user_obj = User.query.filter_by(email=user_data.get("email")).first()
        is_admin = bool(current_user_obj and current_user_obj.is_admin)

    # Catálogo de badges
    if is_admin:
        badges = Badge.query.order_by(Badge.name.asc()).all()
    else:
        badges = Badge.query.filter_by(is_active=True).order_by(Badge.name.asc()).all()

    # Usuários ativos para o select de atribuição
    users = User.query.filter_by(is_active=True).order_by(User.name.asc()).all() if is_admin else []
    partners = AcademicPartner.query.filter_by(is_active=True).order_by(AcademicPartner.name.asc()).all()

    # Listagem de atribuições recentes / existentes
    user_badges_query = UserBadge.query.order_by(UserBadge.issued_at.desc(), UserBadge.id.desc())
    if not is_admin and current_user_obj:
        user_badges_query = user_badges_query.filter_by(user_id=current_user_obj.id)
    user_badges = user_badges_query.limit(100).all()

    return render_template(
        "badges.html",
        badges=badges,
        user_badges=user_badges,
        users=users,
        partners=partners,
        is_admin=is_admin,
        current_user=user_data,
        today_date=datetime.utcnow().strftime("%Y-%m-%d")
    )


@badges_bp.route("/api/<int:badge_id>", methods=["GET"])
def get_badge_api(badge_id):
    """Retorna detalhes de uma badge específica."""
    badge = db.session.get(Badge, badge_id)
    if not badge:
        return jsonify({"error": "Badge não encontrada."}), 404
    return jsonify(badge.to_dict()), 200


@badges_bp.route("/api", methods=["POST"])
@admin_required
def create_badge():
    """Cria uma nova badge no catálogo."""
    data = request.get_json() or request.form
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip() or None
    image_url = (data.get("image_url") or "").strip() or None
    criteria_url = (data.get("criteria_url") or "").strip() or None
    issuer_name = (data.get("issuer_name") or "").strip() or None
    partner_id = data.get("partner_id")

    if not code or not name:
        return jsonify({"error": "Código e nome da badge são obrigatórios."}), 400

    if Badge.query.filter_by(code=code).first():
        return jsonify({"error": f"Já existe uma badge com o código '{code}'."}), 409

    if partner_id:
        try:
            partner_id = int(partner_id)
        except (ValueError, TypeError):
            partner_id = None

    badge = Badge(
        code=code,
        name=name,
        description=description,
        image_url=image_url,
        criteria_url=criteria_url,
        partner_id=partner_id,
        issuer_name=issuer_name,
        is_active=True
    )
    db.session.add(badge)
    db.session.commit()

    return jsonify({"message": f"Badge '{badge.name}' criada com sucesso!", "badge": badge.to_dict()}), 201


@badges_bp.route("/api/<int:badge_id>", methods=["PUT", "POST"])
@admin_required
def update_badge(badge_id):
    """Atualiza dados cadastrais de uma badge."""
    badge = db.session.get(Badge, badge_id)
    if not badge:
        return jsonify({"error": "Badge não encontrada."}), 404

    data = request.get_json() or request.form

    if "name" in data and data["name"].strip():
        badge.name = data["name"].strip()
    if "description" in data:
        badge.description = data["description"].strip() if data["description"] else None
    if "image_url" in data:
        badge.image_url = data["image_url"].strip() if data["image_url"] else None
    if "criteria_url" in data:
        badge.criteria_url = data["criteria_url"].strip() if data["criteria_url"] else None
    if "issuer_name" in data:
        badge.issuer_name = data["issuer_name"].strip() if data["issuer_name"] else None
    if "partner_id" in data:
        p_id = data["partner_id"]
        try:
            badge.partner_id = int(p_id) if p_id else None
        except (ValueError, TypeError):
            badge.partner_id = None
    if "is_active" in data:
        val = data["is_active"]
        badge.is_active = (val is True or val == "true" or val == "1" or val == 1)

    db.session.commit()
    return jsonify({"message": f"Badge '{badge.name}' atualizada com sucesso!", "badge": badge.to_dict()}), 200


@badges_bp.route("/api/<int:badge_id>", methods=["DELETE"])
@admin_required
def delete_badge(badge_id):
    """Exclusão LÓGICA (Soft Delete) de uma badge do catálogo."""
    badge = db.session.get(Badge, badge_id)
    if not badge:
        return jsonify({"error": "Badge não encontrada."}), 404

    badge.is_active = False
    db.session.commit()
    return jsonify({"message": f"Badge '{badge.name}' desativada com sucesso (exclusão lógica).", "badge": badge.to_dict()}), 200


@badges_bp.route("/api/assign", methods=["POST"])
@admin_required
def assign_badge_to_user():
    """
    Pendura uma badge no perfil de um usuário preenchendo obrigatoriamente
    a data de emissão e opcionalmente a data de expiração.
    """
    data = request.get_json() or request.form
    user_id = data.get("user_id")
    badge_id = data.get("badge_id")
    issued_at_str = (data.get("issued_at") or "").strip()
    expires_at_str = (data.get("expires_at") or "").strip() or None
    evidence_url = (data.get("evidence_url") or "").strip() or None

    if not user_id or not badge_id or not issued_at_str:
        return jsonify({"error": "Usuário, Badge e Data de Emissão são obrigatórios."}), 400

    user = db.session.get(User, int(user_id))
    badge = db.session.get(Badge, int(badge_id))

    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404
    if not badge:
        return jsonify({"error": "Badge não encontrada."}), 404

    try:
        issued_at = datetime.strptime(issued_at_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato inválido para Data de Emissão. Use AAAA-MM-DD."}), 400

    expires_at = None
    if expires_at_str:
        try:
            expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d").date()
            if expires_at < issued_at:
                return jsonify({"error": "Data de expiração não pode ser anterior à data de emissão."}), 400
        except ValueError:
            return jsonify({"error": "Formato inválido para Data de Expiração. Use AAAA-MM-DD."}), 400

    # Verifica se já está pendurada
    existing = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
    if existing:
        # Atualiza a emissão existente
        existing.issued_at = issued_at
        existing.expires_at = expires_at
        if evidence_url:
            existing.evidence_url = evidence_url
        db.session.commit()
        return jsonify({
            "message": f"Badge '{badge.name}' já estava associada ao usuário e suas datas foram atualizadas!",
            "user_badge": existing.to_dict()
        }), 200

    user_badge = UserBadge(
        user_id=user.id,
        badge_id=badge.id,
        issued_at=issued_at,
        expires_at=expires_at,
        evidence_url=evidence_url
    )
    db.session.add(user_badge)
    db.session.commit()

    return jsonify({
        "message": f"Badge '{badge.name}' pendurada com sucesso no perfil de {user.name}!",
        "user_badge": user_badge.to_dict()
    }), 201


@badges_bp.route("/api/unassign/<int:user_badge_id>", methods=["DELETE", "POST"])
@admin_required
def unassign_badge(user_badge_id):
    """Remove a badge atribuída a um usuário."""
    ub = db.session.get(UserBadge, user_badge_id)
    if not ub:
        return jsonify({"error": "Atribuição de badge não encontrada."}), 404

    user_name = ub.user.name if ub.user else "Usuário"
    badge_name = ub.badge.name if ub.badge else "Badge"

    db.session.delete(ub)
    db.session.commit()
    return jsonify({"message": f"Badge '{badge_name}' desvinculada do perfil de {user_name} com sucesso."}), 200


@badges_bp.route("/api/sync-credly/<int:user_id>", methods=["POST"])
@admin_required
def sync_credly_manual(user_id):
    """Dispara a sincronização manual do Credly para um usuário específico."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404

    data = request.get_json() or {}
    credly_url = data.get("credly_url") or user.credly_url

    if not credly_url:
        return jsonify({"error": "O usuário não possui uma URL do Credly configurada."}), 400

    result = sync_user_credly_badges(user, credly_url)
    return jsonify(result), (200 if result.get("status") == "success" else 400)

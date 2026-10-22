"""CRUD de Parceiros Acadêmicos (Acesso administrativo para gestão e consulta pública)."""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import AcademicPartner, User
from app.extensions import db
from app.routes.universities import admin_required

partners_bp = Blueprint("partners", __name__, url_prefix="/partners")


@partners_bp.route("/api", methods=["GET"], strict_slashes=False)
def list_partners_api():
    """Retorna lista de parceiros ativos em formato JSON."""
    partners = AcademicPartner.query.filter_by(is_active=True).order_by(AcademicPartner.name.asc()).all()
    return jsonify([p.to_dict() for p in partners]), 200


@partners_bp.route("/", methods=["GET"], strict_slashes=False)
def index_view():
    """Interface de Parceiros Acadêmicos (visão para usuários e controles para admins)."""
    user_data = session.get("user")
    is_admin = False
    if user_data:
        user = User.query.filter_by(email=user_data.get("email")).first()
        is_admin = bool(user and user.is_admin)

    # Se for admin, lista todos (inclusive inativos para reativação); caso contrário apenas ativos
    if is_admin:
        partners = AcademicPartner.query.order_by(AcademicPartner.name.asc()).all()
    else:
        partners = AcademicPartner.query.filter_by(is_active=True).order_by(AcademicPartner.name.asc()).all()

    return render_template(
        "partners.html",
        partners=partners,
        is_admin=is_admin,
        current_user=user_data
    )


@partners_bp.route("/api/<int:partner_id>", methods=["GET"])
@admin_required
def get_partner_api(partner_id):
    """Retorna detalhes de um parceiro específico."""
    partner = AcademicPartner.query.get_or_404(partner_id)
    return jsonify(partner.to_dict()), 200


@partners_bp.route("/api", methods=["POST"])
@admin_required
def create_partner():
    """Cria um novo parceiro acadêmico."""
    data = request.get_json() or request.form
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "CLOUD_TECH").strip().upper()
    website_url = (data.get("website_url") or "").strip() or None
    description = (data.get("description") or "").strip() or None

    if not code or not name:
        return jsonify({"error": "Código e nome do parceiro são obrigatórios."}), 400

    if AcademicPartner.query.filter_by(code=code).first():
        return jsonify({"error": f"Já existe um parceiro com o código '{code}'."}), 409

    partner = AcademicPartner(
        code=code,
        name=name,
        category=category,
        website_url=website_url,
        description=description,
        is_active=True
    )
    db.session.add(partner)
    db.session.commit()
    return jsonify(partner.to_dict()), 201


@partners_bp.route("/api/<int:partner_id>", methods=["PUT", "POST"])
@admin_required
def update_partner(partner_id):
    """Atualiza dados de um parceiro acadêmico existente."""
    partner = AcademicPartner.query.get_or_404(partner_id)
    data = request.get_json() or request.form

    if "name" in data and data["name"].strip():
        partner.name = data["name"].strip()
    if "category" in data and data["category"].strip():
        partner.category = data["category"].strip().upper()
    if "website_url" in data:
        partner.website_url = data["website_url"].strip() or None
    if "description" in data:
        partner.description = data["description"].strip() or None
    if "is_active" in data:
        val = data["is_active"]
        partner.is_active = (val is True or val == "true" or val == "1" or val == 1)

    db.session.commit()
    return jsonify(partner.to_dict()), 200


@partners_bp.route("/api/<int:partner_id>", methods=["DELETE"])
@admin_required
def delete_partner(partner_id):
    """Exclusão LÓGICA (Soft Delete): Desativa o parceiro acadêmico sem apagar dados históricos."""
    partner = AcademicPartner.query.get_or_404(partner_id)
    partner.is_active = False
    db.session.commit()
    return jsonify({
        "message": f"Parceiro {partner.name} ({partner.code}) foi desativado com sucesso (exclusão lógica).",
        "partner": partner.to_dict()
    }), 200

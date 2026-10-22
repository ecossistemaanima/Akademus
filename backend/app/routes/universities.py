"""CRUD de Universidades (Exclusivo para Administrador) e listagem pública de instituições."""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import University, User
from app.extensions import db
from functools import wraps

universities_bp = Blueprint("universities", __name__, url_prefix="/universities")


def admin_required(f):
    """Decorator para exigir autenticação com papel ADMINISTRADOR."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_data = session.get("user")
        if not user_data:
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=user_data.get("email")).first()
        if not user or not user.is_admin:
            return jsonify({"error": "Acesso não autorizado. Perfil de Administrador obrigatório."}), 403
        return f(*args, **kwargs)
    return decorated_function


@universities_bp.route("/api", methods=["GET"])
def list_universities_api():
    """Retorna lista de universidades ativas em formato JSON."""
    unis = University.query.filter_by(is_active=True).order_by(University.name.asc()).all()
    return jsonify([u.to_dict() for u in unis]), 200


@universities_bp.route("/", methods=["GET"])
@admin_required
def index_view():
    """Interface administrativa para gerenciar universidades."""
    unis = University.query.order_by(University.name.asc()).all()
    return render_template("universities.html", universities=unis, current_user=session.get("user"))


@universities_bp.route("/api", methods=["POST"])
@admin_required
def create_university():
    """Cria uma nova universidade."""
    data = request.get_json() or request.form
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    short_name = (data.get("short_name") or "").strip()

    if not code or not name or not short_name:
        return jsonify({"error": "Código, nome e nome curto são obrigatórios."}), 400

    if University.query.filter_by(code=code).first():
        return jsonify({"error": f"Já existe uma universidade com o código {code}."}), 409

    uni = University(code=code, name=name, short_name=short_name, is_active=True)
    db.session.add(uni)
    db.session.commit()
    return jsonify(uni.to_dict()), 201


@universities_bp.route("/api/<int:uni_id>", methods=["GET"])
@admin_required
def get_university_api(uni_id):
    """Retorna detalhes de uma universidade específica."""
    uni = University.query.get_or_404(uni_id)
    return jsonify(uni.to_dict()), 200


@universities_bp.route("/api/<int:uni_id>", methods=["PUT", "POST"])
@admin_required
def update_university(uni_id):
    """Atualiza dados de uma universidade existente."""
    uni = University.query.get_or_404(uni_id)
    data = request.get_json() or request.form

    if "name" in data and data["name"].strip():
        uni.name = data["name"].strip()
    if "short_name" in data and data["short_name"].strip():
        uni.short_name = data["short_name"].strip()
    if "is_active" in data:
        val = data["is_active"]
        uni.is_active = (val is True or val == "true" or val == "1" or val == 1)

    db.session.commit()
    return jsonify(uni.to_dict()), 200


@universities_bp.route("/api/<int:uni_id>", methods=["DELETE"])
@admin_required
def delete_university(uni_id):
    """Exclusão LÓGICA (Soft Delete): Desativa a universidade mantendo a integridade referencial."""
    uni = University.query.get_or_404(uni_id)
    uni.is_active = False
    db.session.commit()
    return jsonify({
        "message": f"Universidade {uni.short_name} ({uni.code}) foi desativada com sucesso (exclusão lógica).",
        "university": uni.to_dict()
    }), 200

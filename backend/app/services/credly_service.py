"""Serviço de sincronização automática com a API pública do Credly."""

import re
import requests
from datetime import datetime
from app.models import Badge, UserBadge, AcademicPartner, User
from app.extensions import db


def extract_credly_username(url_or_username: str) -> str:
    """Extrai o username a partir de URLs como https://www.credly.com/users/hpoyatos/badges ou retorna a string pura."""
    if not url_or_username:
        return ""
    clean = url_or_username.strip()
    match = re.search(r"credly\.com/users/([^/]+)", clean)
    if match:
        return match.group(1)
    return clean.replace("/", "")


def sync_user_credly_badges(user: User, credly_url: str = None) -> dict:
    """
    Lê a página pública do Credly (JSON endpoint), cadastra as badges no catálogo
    se ainda não existirem, e pendura as badges no perfil do usuário com issued_at e expires_at.
    """
    url_to_use = credly_url or user.credly_url
    if not url_to_use:
        return {"status": "error", "message": "Nenhuma URL do Credly fornecida.", "imported": 0}

    username = extract_credly_username(url_to_use)
    if not username:
        return {"status": "error", "message": "Não foi possível identificar o usuário Credly.", "imported": 0}

    endpoint = f"https://www.credly.com/users/{username}/badges.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Akademus-Sync/1.0"
    }

    try:
        resp = requests.get(endpoint, headers=headers, timeout=12)
        if resp.status_code != 200:
            return {
                "status": "error",
                "message": f"Erro ao acessar Credly ({resp.status_code}). Verifique se o perfil é público.",
                "imported": 0
            }

        payload = resp.json()
        badges_data = payload.get("data", [])
        if not badges_data:
            return {"status": "success", "message": "Nenhuma badge pública encontrada no perfil.", "imported": 0}

        imported_count = 0

        for item in badges_data:
            tmpl = item.get("badge_template", {})
            name = tmpl.get("name", "").strip()
            if not name:
                continue

            # Gera código unificado para o catálogo
            slug = tmpl.get("vanity_slug") or name.lower().replace(" ", "_")
            code = re.sub(r"[^A-Za-z0-9_]", "", slug).upper()[:128]

            # Identifica Emissor / Parceiro
            issuer_name = "Credly Issuer"
            entities = item.get("issuer", {}).get("entities", [])
            if entities:
                issuer_name = entities[0].get("entity", {}).get("name", issuer_name)

            # Tenta vincular com academic_partners cadastrados
            partner = AcademicPartner.query.filter(
                (AcademicPartner.name.ilike(f"%{issuer_name}%")) |
                (AcademicPartner.code.ilike(f"%{issuer_name[:4]}%"))
            ).first()

            # Busca ou cria no catálogo de Badges
            badge = Badge.query.filter_by(code=code).first()
            if not badge:
                image_url = item.get("image_url") or tmpl.get("image_url")
                badge = Badge(
                    code=code,
                    name=name,
                    description=tmpl.get("description"),
                    image_url=image_url,
                    criteria_url=tmpl.get("url"),
                    partner_id=partner.id if partner else None,
                    issuer_name=issuer_name,
                    is_active=True
                )
                db.session.add(badge)
                db.session.flush()

            # Processa datas de emissão e expiração
            issued_str = item.get("issued_at_date")
            issued_at = datetime.strptime(issued_str, "%Y-%m-%d").date() if issued_str else datetime.utcnow().date()

            expires_str = item.get("expires_at_date")
            expires_at = datetime.strptime(expires_str, "%Y-%m-%d").date() if expires_str else None

            # Verifica se já está pendurada para este usuário com esta data
            existing_ub = UserBadge.query.filter_by(
                user_id=user.id,
                badge_id=badge.id,
                issued_at=issued_at
            ).first()

            if not existing_ub:
                user_badge = UserBadge(
                    user_id=user.id,
                    badge_id=badge.id,
                    issued_at=issued_at,
                    expires_at=expires_at,
                    credly_badge_id=item.get("id"),
                    evidence_url=f"https://www.credly.com/users/{username}/badges"
                )
                db.session.add(user_badge)
                imported_count += 1

        db.session.commit()
        return {
            "status": "success",
            "message": f"{imported_count} novas badges sincronizadas com sucesso!",
            "imported": imported_count,
            "total_found": len(badges_data)
        }

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Falha na sincronização: {str(e)}", "imported": 0}

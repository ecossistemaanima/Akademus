"""Serviço de extração e sincronização de badges do Google Skills Boost (skills.google)."""

import re
import html
import requests
from datetime import datetime
from app.models import Badge, UserBadge, AcademicPartner, User
from app.extensions import db


def clean_google_skills_url(url_or_id: str) -> str:
    """Normaliza URLs antigas ou novas de perfis públicos do Google Skills."""
    if not url_or_id:
        return ""
    clean = url_or_id.strip()
    match = re.search(r"public_profiles/([a-zA-Z0-9\-]+)", clean)
    if match:
        profile_id = match.group(1)
        return f"https://www.skills.google/public_profiles/{profile_id}"
    return clean


def parse_earned_date(date_str: str) -> datetime.date:
    """Converte datas como 'Earned Oct 21, 2026 EDT' ou 'Earned Feb  2, 2024 EST' para objeto date."""
    if not date_str:
        return datetime.utcnow().date()
    # Remove 'Earned' e timezones (EDT, EST, UTC, etc)
    clean = re.sub(r"Earned\s+", "", date_str.strip())
    clean = re.sub(r"\s+[A-Z]{3,4}$", "", clean)
    clean = re.sub(r"\s+", " ", clean)

    formats = ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            continue
    return datetime.utcnow().date()


def extract_badges_from_html(html_content: str, default_url: str) -> list:
    """Extrai informações estruturadas de badges e descrições de modais usando expressões regulares."""
    # 1. Mapeamento de descrições dos modais <ql-dialog ... id='...'> <p>...</p> </ql-dialog>
    dialog_map = {}
    dialog_matches = re.findall(
        r"<ql-dialog[^>]*?id=['\"]([^'\"]+)['\"][^>]*>([\s\S]*?)</ql-dialog>",
        html_content,
        re.IGNORECASE
    )
    for d_id, d_content in dialog_matches:
        p_match = re.search(r"<p>([\s\S]*?)</p>", d_content, re.IGNORECASE)
        if p_match:
            # Limpa tags html internas e entidades
            desc_text = re.sub(r"<[^>]+>", "", p_match.group(1)).strip()
            dialog_map[d_id] = html.unescape(desc_text)

    # 2. Extração dos blocos <div class='profile-badge'> ... </div>
    # Encontra cada badge individualmente
    badges = []
    badge_blocks = re.findall(
        r"<div\s+class=['\"][^'\"]*profile-badge[^'\"]*['\"][^>]*>([\s\S]*?)(?=<div\s+class=['\"][^'\"]*profile-badge|<div\s+class=['\"][^'\"]*profile-|<main|</main|$)",
        html_content,
        re.IGNORECASE
    )

    for block in badge_blocks:
        # Título
        title_match = re.search(r"<span\s+class=['\"][^'\"]*ql-title-medium[^'\"]*['\"][^>]*>([\s\S]*?)</span>", block, re.IGNORECASE)
        if not title_match:
            continue
        name = html.unescape(re.sub(r"<[^>]+>", "", title_match.group(1)).strip())
        if not name:
            continue

        # Imagem
        img_match = re.search(r"<img[^>]+src=['\"]([^'\"]+)['\"]", block, re.IGNORECASE)
        image_url = html.unescape(img_match.group(1).strip()) if img_match else None

        # Link de evidência
        link_match = re.search(r"<a\s+class=['\"][^'\"]*badge-image[^'\"]*['\"][^>]*href=['\"]([^'\"]+)['\"]", block, re.IGNORECASE)
        evidence_url = html.unescape(link_match.group(1).strip()) if link_match else default_url

        # Data de emissão
        date_match = re.search(r"<span\s+class=['\"][^'\"]*ql-body-medium[^'\"]*['\"][^>]*>([\s\S]*?)</span>", block, re.IGNORECASE)
        date_str = html.unescape(re.sub(r"<[^>]+>", "", date_match.group(1)).strip()) if date_match else ""
        issued_at = parse_earned_date(date_str)

        # Modal de descrição
        modal_match = re.search(r"modal=['\"]([^'\"]+)['\"]", block, re.IGNORECASE)
        modal_id = modal_match.group(1) if modal_match else None
        description = dialog_map.get(modal_id, "Insígnia oficial de capacitação emitida pelo Google Cloud / Google Skills.")

        badges.append({
            "name": name,
            "image_url": image_url,
            "evidence_url": evidence_url,
            "issued_at": issued_at,
            "description": description
        })

    return badges


def sync_user_google_skills_badges(user: User, google_skills_url: str = None) -> dict:
    """
    Lê a página pública do Google Skills Boost (skills.google / cloudskillsboost.google),
    extrai as badges conquistadas (com imagem, título, data de emissão e modal de detalhes),
    cadastra no catálogo de Badges se não existirem e pendura no perfil do usuário.
    """
    url_to_use = google_skills_url or user.google_skills_boost_url
    if not url_to_use:
        return {"status": "error", "message": "Nenhuma URL do Google Skills fornecida.", "imported": 0}

    normalized_url = clean_google_skills_url(url_to_use)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Akademus-Skills/1.0"
    }

    try:
        resp = requests.get(normalized_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return {
                "status": "error",
                "message": f"Erro ao acessar Google Skills ({resp.status_code}). Verifique se o perfil é público.",
                "imported": 0
            }

        badges_extracted = extract_badges_from_html(resp.text, normalized_url)
        if not badges_extracted:
            return {"status": "success", "message": "Nenhuma badge pública encontrada no perfil.", "imported": 0}

        partner = AcademicPartner.query.filter_by(code="GOOGLE_CLOUD").first()
        imported_count = 0

        for item in badges_extracted:
            name = item["name"]
            # Slug unificado (prefixo GSB_)
            slug = re.sub(r"[^A-Za-z0-9_]", "", name.upper().replace(" ", "_"))[:100]
            code = f"GSB_{slug}"

            badge = Badge.query.filter_by(code=code).first()
            if not badge:
                badge = Badge(
                    code=code,
                    name=name,
                    description=item["description"],
                    image_url=item["image_url"],
                    criteria_url=item["evidence_url"],
                    partner_id=partner.id if partner else None,
                    issuer_name="Google Cloud",
                    is_active=True
                )
                db.session.add(badge)
                db.session.flush()

            # Pendura a badge no usuário se ainda não estiver associada com esta data
            existing_ub = UserBadge.query.filter_by(
                user_id=user.id,
                badge_id=badge.id,
                issued_at=item["issued_at"]
            ).first()

            if not existing_ub:
                user_badge = UserBadge(
                    user_id=user.id,
                    badge_id=badge.id,
                    issued_at=item["issued_at"],
                    expires_at=None,
                    evidence_url=item["evidence_url"]
                )
                db.session.add(user_badge)
                imported_count += 1

        db.session.commit()
        return {
            "status": "success",
            "message": f"{imported_count} novas badges do Google Skills sincronizadas com sucesso!",
            "imported": imported_count,
            "total_found": len(badges_extracted)
        }

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Falha na extração do Google Skills: {str(e)}", "imported": 0}

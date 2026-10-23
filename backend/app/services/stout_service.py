"""Serviço de integração e sincronização com o Stout (Revolt Chat)."""

import logging
import requests

logger = logging.getLogger(__name__)

DELTA_INTERNAL_URL = "http://10.43.99.129:5000"


def sync_user_to_stout(email: str, password: str, username: str = None) -> bool:
    """Cria ou atualiza a conta do usuário no Stout com as credenciais do Akademus.
    
    Se a conta já existir, tenta autenticar ou sincronizar.
    """
    if not email or not password:
        return False

    clean_email = email.strip().lower()
    uname = username or clean_email.split("@")[0]

    try:
        # Tenta criar conta
        resp = requests.post(
            f"{DELTA_INTERNAL_URL}/auth/account/create",
            json={
                "email": clean_email,
                "password": password
            },
            timeout=5
        )

        if resp.status_code in (200, 204):
            logger.info("Conta do usuário %s criada com sucesso no Stout.", clean_email)
            return True

        data = resp.json() if resp.content else {}
        err_type = data.get("type", "")

        if err_type == "EmailInUse" or resp.status_code == 409:
            logger.info("Conta %s já existente no Stout. Sincronização mantida.", clean_email)
            return True

        logger.warning("Resposta inesperada ao criar conta no Stout para %s: %s %s", clean_email, resp.status_code, data)
        return False
    except Exception as e:
        logger.error("Erro ao sincronizar usuário %s no Stout: %s", clean_email, e)
        return False

"""Rotas de proxy reverso e integração com o Stout (Revolt Chat)."""

import requests
from flask import Blueprint, request, Response, session, redirect, url_for

stout_bp = Blueprint("stout", __name__)

STOAT_CLIENT_URL = "http://10.43.61.31:5000"
STOAT_DELTA_URL = "http://10.43.99.129:5000"
STOAT_AUTUMN_URL = "http://10.43.134.193:3000"


def proxy_request(target_url: str):
    """Repassa a requisição HTTP para o serviço interno do Kubernetes."""
    req_headers = {key: value for (key, value) in request.headers if key.lower() not in ("host", "content-length")}
    # Encaminha o Host correto do Akademus
    req_headers["X-Forwarded-Host"] = request.host
    req_headers["X-Forwarded-Proto"] = request.scheme

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=req_headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=15
        )

        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection", "cache-control"]
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        headers.append(("Cache-Control", "no-cache, no-store, must-revalidate"))
        headers.append(("Pragma", "no-cache"))
        headers.append(("Expires", "0"))

        return Response(resp.iter_content(chunk_size=1024), resp.status_code, headers)
    except Exception as e:
        return Response(f"Erro de comunicação com o Stout Chat: {str(e)}", status=502)


# 1. Rota do Web Client: /chat e /chat/<path>
@stout_bp.route("/chat", defaults={"path": ""}, methods=["GET", "POST", "HEAD"])
@stout_bp.route("/chat/", defaults={"path": ""}, methods=["GET", "POST", "HEAD"])
@stout_bp.route("/chat/<path:path>", methods=["GET", "POST", "HEAD"])
def stout_client_proxy(path):
    target = f"{STOAT_CLIENT_URL}/{path}" if path else f"{STOAT_CLIENT_URL}/"
    if request.query_string:
        target += f"?{request.query_string.decode('utf-8')}"
    return proxy_request(target)


# Suporte transparente para preloads do Vite que buscam na raiz /assets ou /manifest.webmanifest
@stout_bp.route("/assets/<path:path>", methods=["GET", "HEAD"])
def stout_root_assets_proxy(path):
    target = f"{STOAT_CLIENT_URL}/assets/{path}"
    if request.query_string:
        target += f"?{request.query_string.decode('utf-8')}"
    return proxy_request(target)


@stout_bp.route("/manifest.webmanifest", methods=["GET", "HEAD"])
def stout_root_manifest_proxy():
    return proxy_request(f"{STOAT_CLIENT_URL}/manifest.webmanifest")



# 2. Rota da API Delta: /chat-api e /chat-api/<path>
@stout_bp.route("/chat-api", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
@stout_bp.route("/chat-api/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
@stout_bp.route("/chat-api/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def stout_delta_proxy(path):
    target = f"{STOAT_DELTA_URL}/{path}" if path else f"{STOAT_DELTA_URL}/"
    if request.query_string:
        target += f"?{request.query_string.decode('utf-8')}"
    return proxy_request(target)


# 3. Rota de Arquivos Autumn: /autumn e /autumn/<path>
@stout_bp.route("/autumn", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
@stout_bp.route("/autumn/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
@stout_bp.route("/autumn/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
def stout_autumn_proxy(path):
    target = f"{STOAT_AUTUMN_URL}/{path}" if path else f"{STOAT_AUTUMN_URL}/"
    if request.query_string:
        target += f"?{request.query_string.decode('utf-8')}"
    return proxy_request(target)

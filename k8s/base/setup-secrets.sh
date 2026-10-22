#!/usr/bin/env bash
# ==============================================================================
# Script seguro para provisionar Secrets locais no K3s (Gentoo / Debian)
# NUNCA comite valores de produção ou execute com credenciais padrão em prod.
# ==============================================================================

set -euo pipefail

NAMESPACE="akademus"

echo "➡️ Criando namespace '$NAMESPACE' se não existir..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

read -rsp "Digite a senha do usuário MariaDB (akademus): " MARIADB_PASS
echo
read -rsp "Digite a senha de root do MariaDB: " MARIADB_ROOT_PASS
echo

FLASK_SECRET_KEY=$(openssl rand -hex 32)

echo "➡️ Aplicando Secret 'mariadb-secrets'..."
kubectl create secret generic mariadb-secrets \
  --namespace="$NAMESPACE" \
  --from-literal=mariadb-password="$MARIADB_PASS" \
  --from-literal=mariadb-root-password="$MARIADB_ROOT_PASS" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "➡️ Aplicando Secret 'akademus-flask-secrets'..."
kubectl create secret generic akademus-flask-secrets \
  --namespace="$NAMESPACE" \
  --from-literal=secret-key="$FLASK_SECRET_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Segredos criados com sucesso no K3s! Nada foi salvo em arquivos ou Git."

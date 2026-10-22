# 🔐 Gerenciamento de Segredos e Credenciais (K3s Secrets)

> **Regra de Ouro:** NENHUMA senha, token ou chave privada deve ser commitada no GitHub. O repositório público/privado armazena apenas manifestos com referências ou arquivos `.env.example`.

---

## 🛡️ Estratégia de Segredos no K3s

As credenciais do **Akademus** são gerenciadas diretamente no cluster local **K3s** através de **Kubernetes Secrets**:

### 1. Secret do MariaDB (Namespace: `akademus`)

Criado localmente via linha de comando ou via script de provisionamento seguro:

```bash
kubectl create namespace akademus --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic mariadb-secrets \
  --namespace=akademus \
  --from-literal=mariadb-root-password="SUA_SENHA_ROOT_FORTE" \
  --from-literal=mariadb-password="SUA_SENHA_USUARIO_FORTE" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Secret da Aplicação Flask

Armazena as chaves de sessão e a URI de conexão gerada:

```bash
kubectl create secret generic akademus-flask-secrets \
  --namespace=akademus \
  --from-literal=secret-key="$(openssl rand -hex 32)" \
  --from-literal=db-password="SUA_SENHA_USUARIO_FORTE" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Integração com HashiCorp Vault / External Secrets (Evolução Futura)
Para ambientes distribuídos (Gentoo `development` e Debian `lothlorien` em `main`), o cluster pode utilizar o **External Secrets Operator (ESO)** conectado a uma instância Vault ou Bitwarden Secrets Manager, sincronizando os Secrets do K3s automaticamente sem interação manual.

# 🌐 Ambientes, Git Branching & CI/CD com GitHub Actions

O ciclo de vida de desenvolvimento do **Akademus** utiliza o **GitHub** como versionador oficial de código-fonte, aplicando GitFlow simplificado e esteira de CI/CD integrada a Self-Hosted Runners.

---

## 🌿 Estrutura de Branches & Ambientes

| Branch | Ambiente | Host / Servidor | Domínio / Acesso | Finalidade |
| :--- | :--- | :--- | :--- | :--- |
| `development` | **Development** | **Gentoo Linux** (Local) | `akademus.tux.me.uk` (via Cloudflare) | Desenvolvimento ativo, testes e validação contínua |
| `main` | **Production** | **Debian** (`lothlorien`) | Domínio de Produção | Versão estável em produção acadêmica |

---

## 🔄 Fluxo de Versionamento no GitHub

1. Todo código é desenvolvido localmente orientado a testes (**TDD**).
2. Pull Requests ou pushes na branch `development` disparam o workflow de CI no GitHub Actions.
3. Após aprovação e merge para `main`, a versão é promovida para o ambiente oficial de produção (`lothlorien`).

---

## 🤖 GitHub Actions com Self-Hosted Runner (Gentoo Local)

Para o ambiente de desenvolvimento no Gentoo local, configuramos um **GitHub Self-Hosted Runner**:

```mermaid
flowchart TD
    Dev["Developer (Vibe Coding / Antigravity)"] -->|git push development| GH["GitHub Repository"]
    GH -->|Trigger Workflow| Runner["Self-Hosted Runner (Gentoo Local)"]
    Runner -->|1. Testes TDD (pytest)| Tests["Suíte Pytest"]
    Tests -->|2. Build Container| Build["K3s / Container Build"]
    Build -->|3. Deploy k3s| K3s["K3s Pods (Flask + MariaDB + Stout)"]
    K3s -->|Túnel Seguro| CF["Cloudflare (akademus.tux.me.uk)"]
```

### Exemplo de Workflow (`.github/workflows/dev-ci.yml`)

```yaml
name: CI/CD - Development (Gentoo)

on:
  push:
    branches: [ "development" ]

jobs:
  test-and-deploy:
    runs-on: self-hosted
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Executar Testes TDD
        run: |
          cd backend
          source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate
          pip install -r requirements.txt
          pytest

      - name: Aplicar Manifestos no K3s Local
        run: |
          kubectl apply -f k8s/mariadb/
          kubectl apply -f k8s/app/
```

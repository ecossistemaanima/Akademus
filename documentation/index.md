# 📚 Documentação do Akademus

Bem-vindo à documentação oficial do projeto **Akademus**.

Esta documentação foi projetada utilizando padrões compatíveis com o **GitHub** e preparada para publicação estática (Markdown / GitHub Pages / MkDocs / Docsify).

---

## 🗂️ Estrutura de Documentação

A documentação está organizada nas seguintes seções:

```text
documentation/
├── index.md                 # Este documento (visão geral)
├── database-schema.md       # Modelagem relacional MariaDB, Diagrama ER e regras
├── environments.md          # Ambientes (Gentoo dev vs Debian prod) e CI/CD GitHub Actions
├── architecture.md          # Arquitetura geral, k3s, Cloudflare e infraestrutura
├── backend.md               # Backend Python, Flask, MariaDB e APIs
├── tdd.md                   # Metodologia TDD, Red-Green-Refactor e pytest
├── secrets.md               # Gestão de segredos com K3s Secrets (sem senhas no Git)
├── google-oauth.md          # Passo a passo de configuração do Google OAuth 2.0
├── stout.md                 # Mensageria soberana com Revolt / Stout e integração
└── bot-jocasta.md           # JocastaBOT, regras da comunidade e moderação
```

---

## 📌 Links Rápidos

1. [Arquitetura & Infraestrutura](file:///home/hpoyatos/CodeProjects/Akademus/documentation/architecture.md)
   - Cluster Kubernetes (k3s) em Debian local.
   - Borda e túneis seguros via Cloudflare.
2. [Backend & Persistência](file:///home/hpoyatos/CodeProjects/Akademus/documentation/backend.md)
   - Serviços em **Python** utilizando **Flask**.
   - Modelagem e banco de dados relacional com **MariaDB**.
3. [Chat & Mensageria (Stout / Revolt)](file:///home/hpoyatos/CodeProjects/Akademus/documentation/stout.md)
   - Plataforma de conversação independente de big techs.
   - Organização de canais, categorias de turmas e acessos.
4. [JocastaBOT & Governança](file:///home/hpoyatos/CodeProjects/Akademus/documentation/bot-jocasta.md)
   - Automação de moderação, proteção da comunidade e dinâmicas pedagógicas gamificadas.

---

## 💡 Práticas de Publicação (GitHub Pages)

Para hospedar esta documentação via GitHub Pages, são recomendadas duas abordagens nativas:
1. **GitHub Pages Nativo com Jekyll/Markdown:** Publicação direta a partir da branch principal apontando para a pasta `/docs` ou `/documentation` (via workflow de GitHub Actions).
2. **Geradores Modernos (Recomendado: MkDocs Material ou Docsify):**
   - Renderização limpa, busca rápida e suporte nativo a temas escuros e diagramas Mermaid.

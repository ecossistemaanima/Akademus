# 🐍 Backend & Banco de Dados (Python, Flask, MariaDB)

Este documento detalha o padrão arquitetural e diretrizes do backend do **Akademus**.

---

## 🛠️ Tecnologias Principais

- **Linguagem:** Python 3.11+
- **Framework Web / API:** [Flask](https://flask.palletsprojects.com/)
- **Banco de Dados Relacional:** [MariaDB](https://mariadb.org/)
- **ORM / Migrações:** SQLAlchemy / Flask-Migrate (Alembic)
- **Containerização:** Docker / Pods k3s

---

## 📐 Estrutura de Pastas do Backend (`/backend`)

O backend adota a arquitetura de *Application Factory* e *Blueprints* para modularidade e testes:

```text
backend/
├── app/
│   ├── __init__.py           # Factory da aplicação Flask
│   ├── config.py             # Configurações de ambiente (Dev, Prod, Test)
│   ├── models/               # Modelos relacionais (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py           # Alunos, Professores, Parceiros
│   │   ├── assessment.py     # Avaliações contínuas e notas
│   │   └── gamification.py   # Pontuações, badges e níveis
│   ├── routes/               # Endpoints organizados por Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py           # Autenticação e sessões
│   │   ├── assessments.py    # APIs de avaliações contínuas
│   │   ├── trainings.py      # Gestão de treinamentos com parceiros
│   │   └── gamification.py   # Rankings, badges e conquistas
│   └── services/             # Regras de negócio e integrações externas
│       ├── __init__.py
│       └── stout_service.py  # Integração com a API do Revolt/Stout
├── migrations/               # Histórico de migrações do MariaDB
├── tests/                    # Testes automatizados (pytest)
├── Dockerfile                # Imagem de produção
├── requirements.txt          # Dependências do Python
└── wsgi.py                   # Ponto de entrada (Gunicorn / uWSGI)
```

---

## 🗄️ Estrutura de Dados (MariaDB)

O MariaDB armazena os dados centrais do ecossistema:
1. **Identidades e Papéis:** Perfis de discentes, docentes e parceiros externos.
2. **Avaliações Contínuas:** Registros de submissões, critérios de rubricas e notas.
3. **Mecanismos de Gamificação:** Pontos de experiência (XP), medalhas conquistadas, desafios semanais e logs de atividades.
4. **Mapeamento de Integração:** Vínculo entre IDs internos do Akademus e identidades do Stout/Revolt.

# 🗄️ Modelagem de Dados & Esquema Relacional do Akademus

Este documento especifica o modelo relacional de banco de dados do **Akademus**, implementado no **MariaDB** e mapeado utilizando **SQLAlchemy** (Python).

---

## 📐 Diagrama Entidade-Relacionamento (Mermaid)

```mermaid
erDiagram
    UNIVERSITIES ||--o{ USER_UNIVERSITIES : "possui associados"
    USERS ||--o{ USER_UNIVERSITIES : "pertence a"
    ROLES ||--o{ USER_ROLES : "atribuída a"
    USERS ||--o{ USER_ROLES : "possui"
    ACADEMIC_PARTNERS ||--o{ BADGES : "emite"
    USERS ||--o{ USER_BADGES : "conquista"
    BADGES ||--o{ USER_BADGES : "atribuída a"

    UNIVERSITIES {
        int id PK
        varchar code UK "Código único (ex: USJT, UAM)"
        varchar name "Nome completo institucional"
        varchar short_name "Nome curto / Sigla de exibição"
        boolean is_active "Status ativo/inativo (Soft Delete)"
        datetime created_at
        datetime updated_at
    }

    ACADEMIC_PARTNERS {
        int id PK
        varchar code UK "Identificador único (ex: GOOGLE_CLOUD, RED_HAT)"
        varchar name "Nome da empresa / organização parceira"
        varchar category "Categoria (CLOUD_AI, NETWORKING, etc)"
        varchar website_url "URL do programa educacional"
        varchar logo_url "URL do logotipo"
        text description "Descrição do treinamento / parceria"
        boolean is_active "Status ativo/inativo (Soft Delete)"
        datetime created_at
        datetime updated_at
    }

    BADGES {
        int id PK
        varchar code UK "Slug único da badge (ex: AWS_CERTIFIED_CLOUD_PRACTITIONER)"
        varchar name "Título da insígnia / certificação"
        text description "Descrição das competências comprovadas"
        varchar image_url "URL da imagem da badge (ex: Credly CDN)"
        varchar criteria_url "URL dos critérios oficiais de emissão"
        int partner_id FK "Vínculo opcional com ACADEMIC_PARTNERS"
        varchar issuer_name "Nome da entidade emissora"
        boolean is_active "Status ativo/inativo (Soft Delete)"
        datetime created_at
        datetime updated_at
    }

    USER_BADGES {
        int id PK
        int user_id FK "Vínculo com USERS"
        int badge_id FK "Vínculo com BADGES"
        date issued_at "Data obrigatória de emissão"
        date expires_at "Data opcional de expiração / validade"
        varchar credly_badge_id "ID único de rastreamento no Credly"
        varchar evidence_url "URL pública de verificação"
        datetime created_at
    }

    USERS {
        int id PK
        varchar name "Nome completo"
        varchar email UK "E-mail principal (Imutável)"
        varchar password_hash "Hash da senha (scrypt / Werkzeug)"
        varchar google_id UK "Google Sub/ID"
        varchar google_picture "URL do avatar recebido pelo Google OAuth"
        mediumblob avatar_data "Dados binários da foto de perfil (Upload no MariaDB)"
        varchar avatar_mime_type "MIME Type (image/png, image/jpeg, etc)"
        varchar credly_url "URL do perfil de Badges Digitais Credly"
        varchar linkedin_url "URL do perfil do LinkedIn"
        varchar google_skills_boost_url "URL pública do Google Cloud Skills Boost"
        text bio "Apresentação e interesses acadêmicos"
        boolean is_profile_public "Controle de visibilidade pública dos links"
        varchar ra "Registro de Aluno (Obrigatório para Aluno)"
        varchar status "PENDING, APPROVED, REJECTED"
        boolean is_active "Exclusão Lógica / Soft Delete"
        datetime created_at
        datetime updated_at
    }

    ROLES {
        int id PK
        varchar name UK "ADMINISTRADOR, PROFESSOR, ALUNO, PARCEIRO"
        varchar description
    }

    USER_UNIVERSITIES {
        int user_id PK, FK
        int university_id PK, FK
        datetime created_at
    }

    USER_ROLES {
        int user_id PK, FK
        int role_id PK, FK
        datetime created_at
    }
```

---

## 🏛️ Convenções e Regras de Negócio Adotadas

1. **Nomenclatura Relacional:**
   - Tabelas em **plural minúsculo com snake_case**: `universities`, `academic_partners`, `users`, `roles`.
   - Tabelas associativas (Many-to-Many): `user_universities`, `user_roles`.
   - Colunas em **snake_case**: `id`, `short_name`, `password_hash`, `google_id`, `credly_url`, `linkedin_url`, `google_skills_boost_url`, `is_profile_public`, `is_active`.
   - Chaves primárias com auto-incremento `id`.
   - Constraints de unicidade explícitas (`unique=True`) em `universities.code`, `academic_partners.code`, `users.email` e `users.google_id`.
   - Chaves estrangeiras com integridade referencial `ON DELETE CASCADE`.

2. **Exclusão Lógica (Soft Delete):**
   - Implementado através da coluna `is_active BOOLEAN NOT NULL DEFAULT TRUE` em `universities`, `academic_partners` e `users`.
   - Nenhuma exclusão física é executada por padrão, garantindo a integridade dos dados históricos pedagógicos e de auditoria.

3. **Política de Senhas:**
   - Senhas locais exigem no mínimo 8 caracteres, com ao menos 1 maiúscula, 1 minúscula, 1 número e 1 caractere especial, validadas com confirmação de senha.

4. **Regra de Visibilidade e Privacidade (Perfil):**
   - Estudantes escolhem se seus links profissionais (`credly_url`, `linkedin_url`, `google_skills_boost_url`) ficam públicos para outros estudantes (`is_profile_public`).
   - Usuários com papéis `ADMINISTRADOR` ou `PROFESSOR` **sempre têm acesso de visualização**, independentemente da opção do aluno.

5. **Hierarquia de Papéis (Roles):**
   - `ADMINISTRADOR`: Acesso total aos CRUDs de Universidades, Usuários e moderação de novos cadastros.
   - `PROFESSOR`: Não possui RA obrigatório; pode lecionar e estar vinculado a múltiplas universidades.
   - `ALUNO`: RA obrigatório no cadastro; vinculado a uma ou mais universidades.
   - `PARCEIRO`: Instrutores e convidados de empresas parceiras.

6. **Status de Autorização:**
   - Todo usuário que se autocadastra (via formulário ou Google OAuth) inicia com `status = 'PENDING'`.
   - O `ADMINISTRADOR` aprova (`APPROVED`) ou rejeita (`REJECTED`) o acesso na tela de moderação `/users`.
   - Usuário admin mestre pré-configurado: `hpoyatos@gmail.com` (aprovado com papéis `ADMINISTRADOR` e `PROFESSOR` e associado a todas as universidades Ânima).

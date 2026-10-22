"""Modelos relacionais do banco de dados do Akademus."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# Tabela Associativa: Usuários <-> Universidades (N:N)
user_universities = db.Table(
    "user_universities",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("university_id", db.Integer, db.ForeignKey("universities.id", ondelete="CASCADE"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow, nullable=False),
)

# Tabela Associativa: Usuários <-> Roles (N:N)
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow, nullable=False),
)


class University(db.Model):
    """Entidade que representa uma Universidade ou Faculdade."""
    __tablename__ = "universities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    short_name = db.Column(db.String(64), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com Usuários
    users = db.relationship("User", secondary=user_universities, back_populates="universities")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "short_name": self.short_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AcademicPartner(db.Model):
    """Entidade que representa um Parceiro Acadêmico (Google Cloud, Red Hat, Cisco, AWS, etc)."""
    __tablename__ = "academic_partners"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(64), default="CLOUD_TECH", nullable=False)
    website_url = db.Column(db.String(512), nullable=True)
    logo_url = db.Column(db.String(512), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "website_url": self.website_url,
            "description": self.description,
            "is_active": self.is_active,
        }


class Badge(db.Model):
    """Catálogo de Badges / Insígnias Digitais de parceiros e capacitações."""
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(128), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    criteria_url = db.Column(db.String(512), nullable=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("academic_partners.id", ondelete="SET NULL"), nullable=True)
    issuer_name = db.Column(db.String(128), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    partner = db.relationship("AcademicPartner", backref=db.backref("badges", lazy="dynamic"))
    user_badges = db.relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "criteria_url": self.criteria_url,
            "partner_id": self.partner_id,
            "partner_name": self.partner.name if self.partner else self.issuer_name,
            "issuer_name": self.issuer_name,
            "is_active": self.is_active,
        }


class UserBadge(db.Model):
    """Emissão de uma Badge para um Usuário com data de emissão e expiração."""
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    issued_at = db.Column(db.Date, nullable=False)
    expires_at = db.Column(db.Date, nullable=True)
    credly_badge_id = db.Column(db.String(128), nullable=True)
    evidence_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("user_badges", cascade="all, delete-orphan", lazy="joined"))
    badge = db.relationship("Badge", back_populates="user_badges", lazy="joined")

    @property
    def is_expired(self) -> bool:
        """Indica se a badge já atingiu a data de validade/expiração."""
        if not self.expires_at:
            return False
        return self.expires_at < datetime.utcnow().date()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "badge_id": self.badge_id,
            "badge": self.badge.to_dict() if self.badge else None,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "evidence_url": self.evidence_url,
            "is_expired": self.is_expired,
        }


class Role(db.Model):
    """Papel / Perfil de acesso do usuário no sistema."""
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship("User", secondary=user_roles, back_populates="roles")


class User(db.Model):
    """Entidade que representa um Usuário (Estudante, Professor, Admin, Parceiro)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)

    # Campos de autenticação Google OAuth
    google_id = db.Column(db.String(128), unique=True, nullable=True, index=True)
    google_picture = db.Column(db.String(512), nullable=True)

    # Avatar armazenado diretamente no banco (Upload em MEDIUMBLOB)
    avatar_data = db.Column(db.LargeBinary(length=16777215), nullable=True)
    avatar_mime_type = db.Column(db.String(64), nullable=True)

    @property
    def avatar_url(self) -> str:
        """Retorna a URL do avatar servida pelo backend se houver BLOB ou fallback para Google/UI-Avatars."""
        if self.avatar_data:
            return f"/users/{self.id}/avatar"
        if self.google_picture:
            return self.google_picture
        import urllib.parse
        encoded_name = urllib.parse.quote(self.name or "User")
        return f"https://ui-avatars.com/api/?name={encoded_name}&background=6366f1&color=fff"

    # Perfis Profissionais e Acadêmicos (Badges, Skills, Redes)
    credly_url = db.Column(db.String(512), nullable=True)
    linkedin_url = db.Column(db.String(512), nullable=True)
    google_skills_boost_url = db.Column(db.String(512), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Controle de Visibilidade: Outros usuários só veem os links profissionais se is_profile_public for True
    # Professores e Administradores sempre podem ver
    is_profile_public = db.Column(db.Boolean, default=False, nullable=False)

    # Registro Acadêmico de Aluno (Obrigatório para alunos, nulo para professores/admins)
    ra = db.Column(db.String(64), nullable=True, index=True)

    # Status de Moderação de Cadastro: PENDING, APPROVED, REJECTED
    status = db.Column(db.String(16), default="PENDING", nullable=False, index=True)

    # Exclusão Lógica (Soft Delete)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    universities = db.relationship("University", secondary=user_universities, back_populates="users")
    roles = db.relationship("Role", secondary=user_roles, back_populates="users")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)

    @property
    def is_admin(self) -> bool:
        return self.has_role("ADMINISTRADOR")

    def to_dict(self, viewer=None):
        """
        Exporta dados do usuário para dicionário.
        Se 'viewer' for passado, oculta URLs profissionais se o perfil for privado,
        exceto se o viewer for o próprio usuário, Administrador ou Professor.
        """
        can_view_private = False
        if viewer:
            if viewer.id == self.id or viewer.is_admin or viewer.has_role("PROFESSOR"):
                can_view_private = True
        else:
            can_view_private = self.is_profile_public

        show_details = self.is_profile_public or can_view_private

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "ra": self.ra,
            "status": self.status,
            "is_active": self.is_active,
            "avatar_url": self.avatar_url,
            "google_picture": self.google_picture,
            "has_custom_avatar": bool(self.avatar_data),
            "bio": self.bio,
            "credly_url": self.credly_url if show_details else None,
            "linkedin_url": self.linkedin_url if show_details else None,
            "google_skills_boost_url": self.google_skills_boost_url if show_details else None,
            "is_profile_public": self.is_profile_public,
            "roles": [r.name for r in self.roles],
            "universities": [u.short_name for u in self.universities],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

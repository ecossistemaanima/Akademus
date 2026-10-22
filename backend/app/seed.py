"""Script de semente inicial (Seed) das Universidades da Ânima Educação e papéis."""

from app.extensions import db
from app.models import University, Role, User

ANIMA_UNIVERSITIES = [
    {"code": "USJT", "name": "Universidade São Judas Tadeu", "short_name": "São Judas"},
    {"code": "UAM", "name": "Universidade Anhembi Morumbi", "short_name": "Anhembi Morumbi"},
    {"code": "UNIBH", "name": "Centro Universitário de Belo Horizonte", "short_name": "UniBH"},
    {"code": "UNA", "name": "Centro Universitário UNA", "short_name": "UNA"},
    {"code": "UNIFACS", "name": "Universidade Salvador", "short_name": "UNIFACS"},
    {"code": "UNP", "name": "Universidade Potiguar", "short_name": "UnP"},
    {"code": "UNISUL", "name": "Universidade do Sul de Santa Catarina", "short_name": "UNISUL"},
    {"code": "UNISOCIESC", "name": "Centro Universitário Sociesc", "short_name": "UniSociesc"},
    {"code": "IBMR", "name": "Centro Universitário IBMR", "short_name": "IBMR"},
    {"code": "UNIRITTER", "name": "Centro Universitário Ritter dos Reis", "short_name": "UniRitter"},
    {"code": "FADERGS", "name": "Centro Universitário FADERGS", "short_name": "FADERGS"},
    {"code": "UNICURITIBA", "name": "Centro Universitário Curitiba", "short_name": "UniCuritiba"},
    {"code": "AGES", "name": "Centro Universitário AGES", "short_name": "AGES"},
    {"code": "UNIFG", "name": "Centro Universitário FG", "short_name": "UniFG"},
    {"code": "FPB", "name": "Faculdade Internacional da Paraíba", "short_name": "FPB"},
    {"code": "MILTON_CAMPOS", "name": "Faculdade de Direito Milton Campos", "short_name": "Milton Campos"},
    {"code": "FASEH", "name": "Faculdade de Saúde e Ecologia Humana", "short_name": "FASEH"},
    {"code": "INSPIRALI", "name": "Inspirali Educação Médica", "short_name": "Inspirali"},
]

DEFAULT_ROLES = [
    {"name": "ADMINISTRADOR", "description": "Acesso total aos CRUDs de Universidades, Usuários e aprovações."},
    {"name": "PROFESSOR", "description": "Docente universitário, cria avaliações e orienta projetos sem exigência de RA."},
    {"name": "ALUNO", "description": "Estudante universitário com RA obrigatório."},
    {"name": "PARCEIRO", "description": "Instrutores ou convidados de empresas e entidades parceiras."},
]


def seed_database(app):
    """Executa a semente de dados no banco."""
    with app.app_context():
        # 1. Garante que as tabelas existem
        db.create_all()

        # 2. Popula Roles
        roles_map = {}
        for r_data in DEFAULT_ROLES:
            role = Role.query.filter_by(name=r_data["name"]).first()
            if not role:
                role = Role(name=r_data["name"], description=r_data["description"])
                db.session.add(role)
                db.session.flush()
            roles_map[role.name] = role

        # 3. Popula Universidades da Ânima Educação
        all_unis = []
        for u_data in ANIMA_UNIVERSITIES:
            uni = University.query.filter_by(code=u_data["code"]).first()
            if not uni:
                uni = University(
                    code=u_data["code"],
                    name=u_data["name"],
                    short_name=u_data["short_name"],
                    is_active=True
                )
                db.session.add(uni)
                db.session.flush()
            all_unis.append(uni)

        # 4. Cria / Atualiza Usuário Mestre (hpoyatos@gmail.com)
        admin_email = "hpoyatos@gmail.com"
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                name="Prof. Henrique Poyatos",
                email=admin_email,
                status="APPROVED",
                ra=None  # Professor / Admin não tem RA
            )
            admin_user.set_password("Admin@Akademus2026!")
            admin_user.roles.append(roles_map["ADMINISTRADOR"])
            admin_user.roles.append(roles_map["PROFESSOR"])
            # Associa o professor a todas as universidades Ânima
            admin_user.universities = all_unis
            db.session.add(admin_user)
        else:
            # Garante que possui as roles e todas as universidades
            if not admin_user.has_role("ADMINISTRADOR"):
                admin_user.roles.append(roles_map["ADMINISTRADOR"])
            admin_user.universities = all_unis
            admin_user.status = "APPROVED"

        db.session.commit()
        print("✅ Banco inicializado com Universidades Ânima, Roles e Usuário Administrador Mestre!")

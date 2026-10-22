"""Factory principal da aplicação Flask do Akademus."""

import os
from flask import Flask, jsonify
from app.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
from app.extensions import db, migrate


def create_app(test_config=None):
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__)

    # Carrega a configuração adequada ao ambiente
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    elif env == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Sobrescreve com configurações específicas passadas para testes
    if test_config:
        app.config.update(test_config)

    # Suporte a Reverse Proxy (Cloudflare Tunnel) para repassar HTTPS e Host corretos
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Força esquema seguro padrão para redirects externos por trás de proxy
    app.config["PREFERRED_URL_SCHEME"] = "https"

    # Inicializa extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)

    # Configura provedor OAuth (Google)
    from app.routes.auth import auth_bp, configure_oauth
    from app.routes.universities import universities_bp
    from app.routes.users import users_bp
    from app.routes.partners import partners_bp
    from app.routes.badges import badges_bp

    configure_oauth(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(universities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(partners_bp)
    app.register_blueprint(badges_bp)

    # Redirecionamento amigável para Meu Perfil
    @app.route("/profile", methods=["GET", "POST"])
    def my_profile_redirect():
        from app.routes.users import edit_my_profile
        return edit_my_profile()

    # Endpoint raiz (Redireciona para /login se não autenticado ou exibe Dashboard)
    @app.route("/", methods=["GET"])
    def index():
        from flask import session, render_template, redirect, url_for
        from app.models import User

        user_session = session.get("user")
        if not user_session:
            return redirect(url_for("auth.login"))

        user_db = User.query.filter_by(email=user_session.get("email")).first()

        return render_template(
            "dashboard.html",
            user=user_session,
            user_db=user_db
        )

    # Endpoint base de verificação de integridade (Health Check)
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "Akademus",
            "environment": "testing" if app.config.get("TESTING") else env
        }), 200

    return app

from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    print(app.config.get("SQLALCHEMY_DATABASE_URI"))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so Flask-Migrate can detect them
    with app.app_context():
        from app.auth.models import User
        from app.interns.models import Intern

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.interns.routes import interns_bp
    from app.uploads.routes import uploads_bp
    from app.reports.routes import reports_bp
    from app.ai.routes import ai_bp
    from app.tasks.routes import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(interns_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(tasks_bp)

    return app
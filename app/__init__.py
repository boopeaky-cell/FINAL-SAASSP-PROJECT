"""
SAASSP - Smart Academic Advisory & Student Success Platform
Application factory.

See SAASSP_SDD.docx Section 3 (Architecture Design) for the component
breakdown this package follows, and SAASSP_SRS.docx Section 3.2 for the
use cases each route implements.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_object=None):
    app = Flask(__name__)

    if config_object is None:
        from config import Config
        config_object = Config
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth import auth_bp
    from app.student import student_bp
    from app.staff import staff_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == "student":
                return redirect(url_for("student.dashboard"))
            if current_user.role == "academic_staff":
                return redirect(url_for("staff.student_list"))
            if current_user.role == "admin":
                return redirect(url_for("admin.programmes"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()

    return app

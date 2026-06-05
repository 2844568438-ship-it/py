import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'


@pytest.fixture
def app():
    """Create test app with in-memory DB"""
    # Set env before importing app modules
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    from models import db as _db
    from flask_login import LoginManager

    app = Flask(__name__)
    app.config.from_object(TestConfig)

    _db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.init_app(app)

    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.patient import patient_bp
    from routes.doctor import doctor_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    # Context processor
    @app.context_processor
    def inject_globals():
        return {'pinned_announcements': []}

    with app.app_context():
        _db.create_all()
        from models import Department, User
        dept = Department(name='内科', description='内科诊疗')
        _db.session.add(dept)
        _db.session.flush()

        admin = User(name='管理员', phone='admin', role='admin', gender='男', age=35)
        admin.set_password('admin123')
        _db.session.add(admin)

        doctor = User(name='张医生', phone='13800000002', role='doctor',
                      department_id=dept.id, title='主任医师',
                      specialty='心血管', gender='男', age=45,
                      consultation_fee=50)
        doctor.set_password('123456')
        _db.session.add(doctor)

        patient = User(name='李患者', phone='13800000001', role='patient',
                       gender='男', age=28)
        patient.set_password('123456')
        _db.session.add(patient)
        _db.session.commit()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    from models import db as _db
    with app.app_context():
        yield _db

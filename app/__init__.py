from flask import Flask
from flask_login import LoginManager
from .models import db, bcrypt, Officer
from config import config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this system.'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .routes.auth import auth_bp
    from .routes.lookup import lookup_bp
    from .routes.offences import offences_bp
    from .routes.payments import payments_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(lookup_bp)
    app.register_blueprint(offences_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return Officer.query.get(int(user_id))

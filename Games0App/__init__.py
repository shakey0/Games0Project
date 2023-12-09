from flask import Flask
from Games0App.extensions import db, migrate
from .config import load_config
import os

def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(load_config(env))

    db.init_app(app)
    migrate.init_app(app, db)

    from .views.main import main as main_blueprint
    from .views.user_profile import user_profile as user_blueprint
    from .views.auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)

    return app

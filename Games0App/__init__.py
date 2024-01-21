from flask import Flask
from flask_login import LoginManager
from Games0App.extensions import db, migrate, count_words, format_date
from .config import load_config
import os

def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(load_config(env))

    app.jinja_env.filters['count_words'] = count_words
    app.jinja_env.filters['format_date'] = format_date

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.index'

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    from .views.main import main as main_blueprint
    from .views.auth import auth as auth_blueprint
    from .views.api import api as api_blueprint
    from .views.scoreboard import scoreboard as scoreboard_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(scoreboard_blueprint)

    return app

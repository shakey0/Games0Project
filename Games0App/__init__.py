from flask import Flask, g, request, make_response, jsonify
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

    @app.before_request
    def check_privacy_policy():
        g.show_privacy_policy = not request.cookies.get('privacy_policy_seen')

    @app.context_processor
    def inject_privacy_policy_flag():
        return dict(show_privacy_policy=g.show_privacy_policy)
    
    @app.route('/acknowledge_privacy_policy')
    def acknowledge_privacy_policy():
        response = make_response(jsonify(message="Privacy policy acknowledged"))
        response.set_cookie('privacy_policy_seen', 'yes', max_age=60*60*24*365*2) # Set cookie for 2 years
        return response

    @app.after_request
    def add_cache_control_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app

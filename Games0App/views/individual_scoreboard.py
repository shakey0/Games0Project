from flask import Blueprint, render_template, request, redirect, flash
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from Games0App.games import games


scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_page():

    token = request.args.get('token')

    if token:
        game_type = redis_client.hget(token, 'game_type').decode('utf-8')
        if not game_type:
            flash("Sorry, your game has expired. Please start again.")
            return redirect('/')
        game = next(item for item in games if item.param == game_type)

        if game.categories:
            category_name = redis_client.hget(token, 'category_name').decode('utf-8')
            game_name = game.name + " - " + category_name
        else:
            game_name = game.name
    
    else:
        game_name = "All Games"

    users = User.query.all()
    return render_template('individual_scoreboard.html', users=users, user=current_user, game_name=game_name)
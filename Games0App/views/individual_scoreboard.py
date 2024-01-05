from flask import Blueprint, render_template, request, redirect, flash
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from Games0App.models.high_score import HighScore, scores_users
from Games0App.games import games
from sqlalchemy.sql import case


scoreboard = Blueprint('scoreboard', __name__)


def get_high_scores(game_name):

    # print(game_name)

    current_user_id = current_user.id if current_user.is_authenticated else 0

    likes_subquery = db.session.query(scores_users).filter(
        scores_users.c.score_id == HighScore.id,
        scores_users.c.user_id == current_user_id
    ).exists().correlate(HighScore)

    # Query to select top 10 high scores with usernames and like status
    high_scores_query = db.session.query(
        HighScore,
        User.username.label('username'),
        case(
            (likes_subquery, True),
            else_=False
        ).label('user_likes_score')
    ).join(
        User, HighScore.user_id == User.id
    ).outerjoin(
        scores_users, (HighScore.id == scores_users.c.score_id) & (scores_users.c.user_id == current_user_id)
    ).filter(
        HighScore.game == game_name
    ).order_by(
        HighScore.score.desc()
    ).limit(10)

    high_scores = high_scores_query.all()
    # print('Current user id:', current_user_id)
    # print(high_scores)
    # print(top_scores_query.statement)
    return high_scores


@scoreboard.route('/scoreboard')
def scoreboard_page():

    token = request.args.get('token')

    if token:
        game_type = redis_client.hget(token, 'game_type')
        if not game_type:
            flash("Sorry, your game has expired. Please start again.")
            return redirect('/')
        else:
            game_type = game_type.decode('utf-8')
        if not game_type:
            flash("Sorry, your game has expired. Please start again.")
            return redirect('/')
        game = next(item for item in games if item.param == game_type)

        if game.categories:
            category_name = redis_client.hget(token, 'category_name').decode('utf-8')
            game_name = game.name + " - " + category_name
            stored_game_name = game.lower_name + "_" + category_name.lower().replace(' ', '').replace('&', '')
        else:
            game_name = game.name
            stored_game_name = game.lower_name
        if "_mc" in game.param:
            difficulty = redis_client.hget(token, 'difficulty').decode('utf-8')
            stored_game_name += "_" + difficulty
    
    else:
        game_type = request.args.get('game_type')
        if not game_type:
            flash("Sorry, something went wrong!")
            return redirect('/')
        game = next(item for item in games if item.param == game_type)

        if game.categories:
            category_name = request.args.get('category_name')
            game_name = game.name + " - " + category_name
            stored_game_name = game.lower_name + "_" + category_name.lower().replace(' ', '').replace('&', '')
        else:
            game_name = game.name
            stored_game_name = game.lower_name
        if "_mc" in game.param:
            difficulty = request.args.get('difficulty')
            stored_game_name += "_" + difficulty

    high_scores = get_high_scores(stored_game_name)

    print(db.session.query(HighScore).all()[0].score)

    return render_template('individual_scoreboard.html', user=current_user, game_name=game_name, game=game,
                            high_scores=high_scores)
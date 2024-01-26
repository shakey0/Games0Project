from flask import Blueprint, render_template, request, redirect, flash, jsonify
from flask_login import current_user, login_required
from Games0App.extensions import db, redis_client
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.views.scoreboard_functions import get_high_scores, get_user_scores, get_all_scores
from Games0App.utils import validate_victory_message
from sqlalchemy import update


scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_page():

    token = request.args.get('token')
    game_name_param = request.args.get('game_name_param')
    username = request.args.get('username')

    if token:
        game_type = redis_client.hget(token, 'game_type')
        if not game_type:
            flash("Sorry, your game has expired. Please start again.")
            return redirect('/')
        else:
            game_type = game_type.decode('utf-8')
        game = next(item for item in games if item.param == game_type)

        if game.categories:
            category_name = redis_client.hget(token, 'category_name').decode('utf-8')
            game_name = game.name + " - " + category_name
        else:
            game_name = game.name

        game_name_param = redis_client.hget(token, 'game_name_param').decode('utf-8')
        high_score_saved = redis_client.hget(token, 'high_score_saved')
        needs_high_score = True if not high_score_saved else False

        high_scores = get_high_scores(game_name_param)
    
    elif game_name_param:
        game_type = game_name_param
        if ("_easy" in game_name_param or "_medium" in game_name_param or "_hard" in game_name_param) \
            and "categories" in game_name_param:
            game_type = game_name_param.rsplit("_", 2)[0]
            category_name = request.args.get('category')
        elif "_easy" in game_name_param or "_medium" in game_name_param or "_hard" in game_name_param:
            game_type = game_name_param.rsplit("_", 1)[0]
        elif "categories" in game_name_param:
            game_type = game_name_param.rsplit("_", 1)[0]
            category_name = request.args.get('category')

        try:
            game = next(item for item in games if item.param == game_type)
        except:
            flash("Sorry, something went wrong!")
            return redirect('/')

        if game.categories:
            game_name = game.name + " - " + category_name
        else:
            game_name = game.name

        needs_high_score = False

        high_scores = get_high_scores(game_name_param)

    elif username:
        game_name = f"{username}'s Scores" if username != current_user.username else "Your Profile & Scores"

        needs_high_score = False

        high_scores = get_user_scores(username)
        if high_scores == None:
            flash("Sorry, something went wrong!")
            return redirect('/')
        
    else:
        game_name = "Scoreboards"

        needs_high_score = False

        high_scores = get_all_scores()

    return render_template('scoreboard.html', user=current_user, game_name=game_name, token=token,
                            all_games_scores=high_scores, needs_high_score=needs_high_score)


@scoreboard.route('/amend_score', methods=['POST'])
@login_required
def amend_score():

    score_id = request.form.get('score_id')
    message = request.form.get('message')

    message_check = validate_victory_message(message)
    if message_check != True:
        return jsonify(success=False, error=message_check)
    
    score = HighScore.query.filter_by(id=score_id, user_id=current_user.id).first()

    if score:
        db.session.execute(update(HighScore).where(HighScore.id == score_id).values(message=message))
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Score not found or access denied"), 403


@scoreboard.route('/delete_score', methods=['POST'])
@login_required
def delete_score():

    score_id = request.form.get('score_id')

    score = HighScore.query.filter_by(id=score_id, user_id=current_user.id).first()

    if score:
        db.session.delete(score)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Score not found or access denied"), 403

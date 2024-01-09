from flask import Blueprint, render_template, request, redirect, flash, jsonify
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.views.route_functions import get_high_scores
from Games0App.utils import format_date, validate_victory_message
from sqlalchemy import update


scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_page():

    token = request.args.get('token')

    difficulty = None

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
            stored_game_name = game.lower_name + "_" + category_name.lower().replace(' ', '').replace('&', '')
        else:
            game_name = game.name
            stored_game_name = game.lower_name
        if "_mc" in game.param:
            difficulty = redis_client.hget(token, 'difficulty').decode('utf-8')
            stored_game_name += "_" + difficulty

        high_score_saved = redis_client.hget(token, 'high_score_saved')
        needs_high_score = True if not high_score_saved else False
    
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

        needs_high_score = False

    high_scores = get_high_scores(stored_game_name)

    if difficulty:
        difficulty = difficulty.title()

    return render_template('scoreboard.html', user=current_user, game_name=game_name, game=game,
                            token=token, high_scores=high_scores, needs_high_score=needs_high_score,
                            format_date=format_date, difficulty=difficulty)


@scoreboard.route('/amend_score', methods=['POST'])
def amend_score():

    score_id = request.form.get('score_id')
    message = request.form.get('message')

    message_check = validate_victory_message(message)
    if message_check != True:
        return jsonify(success=False, error=message_check)
    
    db.session.execute(update(HighScore).where(HighScore.id == score_id).values(message=message))
    db.session.commit()

    return jsonify(success=True)


@scoreboard.route('/delete_score', methods=['POST'])
def delete_score():

    score_id = request.form.get('score_id')

    db.session.delete(HighScore.query.get(score_id))
    db.session.commit()

    return jsonify(success=True)
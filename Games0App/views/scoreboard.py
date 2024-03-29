from flask import Blueprint, render_template, request, redirect, flash, jsonify
from flask_login import current_user, login_required
from Games0App.extensions import db, redis_client
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.views.scoreboard_functions import get_high_scores, get_user_scores, get_all_scores
from Games0App.classes.auth_validator import auth_validator
from Games0App.classes.logger import logger
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
            flash("Sorry! Your game has expired. Please start a new game.", "error")
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
            json_log = {
                'game_name_param': game_name_param
            }
            unique_id = logger.log_event(json_log, 'scoreboard_page', 'game_scoreboard_param_error')
            print("GAME_NAME_PARAM_ERROR: " + unique_id)
            flash("Sorry! Something went wrong.", "error")
            return redirect('/')

        if game.categories:
            game_name = game.name + " - " + category_name
        else:
            game_name = game.name

        needs_high_score = False

        high_scores = get_high_scores(game_name_param)

    elif username:
        game_name = f"{username}'s Scores" if not current_user.is_authenticated or username != current_user.username else "Your Profile & Scores"

        needs_high_score = False

        high_scores = get_user_scores(username)
        if high_scores == None:
            json_log = {
                'username_of_scores': username
            }
            if current_user.is_authenticated:
                json_log['user_id'] = current_user.id
                json_log['username_of_current_user'] = current_user.username
            unique_id = logger.log_event(json_log, 'scoreboard_page', 'user_scoreboard_retrieval_error')
            print("USER_SCOREBOARD_RETRIEVAL_ERROR: " + unique_id)
            flash("Sorry, something went wrong!", "error")
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

    message_check = auth_validator.validate_victory_message()
    if message_check != True:
        return jsonify(success=False, error=message_check)
    
    score_id = request.form.get('score_id')
    score = HighScore.query.filter_by(id=score_id, user_id=current_user.id).first()

    if score:
        db.session.execute(
            update(HighScore).where(HighScore.id == score_id).values(message=request.form.get('message'))
        )
        db.session.commit()
        return jsonify(success=True)
    else:
        json_log = {
            'score_id': score_id,
            'user_id': current_user.id
        }
        unique_id = logger.log_event(json_log, 'amend_score', 'score_not_found')
        print("SCORE_NOT_FOUND_ERROR: " + unique_id)
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
        json_log = {
            'score_id': score_id,
            'user_id': current_user.id
        }
        unique_id = logger.log_event(json_log, 'delete_score', 'score_not_found')
        print("SCORE_NOT_FOUND_ERROR: " + unique_id)
        return jsonify(success=False, message="Score not found or access denied"), 403

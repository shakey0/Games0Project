from flask import request, redirect, flash
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from Games0App.models.high_score import HighScore, scores_users
from Games0App.games import games
from sqlalchemy.sql import case
import json
import random


# For main.py ---------------------------------------------------------------

def get_key_game_data(request_type):

    if request_type == 'GET':
        return None

    token = request.form.get('token')

    game_type = redis_client.hget(token, 'game_type')
    if not game_type:
        return None
    game_type = game_type.decode('utf-8')
    game = next(item for item in games if item.param == game_type)

    category_name = ""
    if game.categories:
        category_name = redis_client.hget(token, 'category_name').decode('utf-8')
        game_name = game.name + " - " + category_name
    else:
        game_name = game.name
        
    return token, game, category_name, game_name


def get_next_question(game, token, question_number, category_name, difficulty):
    next_question = game.get_question(question_number, category=category_name, difficulty=difficulty)
    print('NEXT QUESTION: ', next_question)
    if not next_question:
        flash("Something went wrong.")
        return redirect('/')
    
    redis_client.hset(token, 'question_tracker', next_question["last_question_no"])
    redis_client.hset(token, 'question', next_question["question"])
    redis_client.hset(token, 'answer', next_question["answer"])

    if len(next_question) == 5: # CHANGE TO "wrong answers" in next_question
        next_question["all_answers"] = [next_question["answer"]] + next_question["wrong_answers"]
        random.shuffle(next_question["all_answers"])
        redis_client.hset(token, 'all_answers', json.dumps(next_question["all_answers"]))
    
    return next_question


# For scoreboard.py ---------------------------------------------------------------

def organise_score_data(score_data):

    high_scores_list = []

    for high_score, username, user_likes_score in score_data:
        score_dict = {
            'score_id': high_score.id,
            'user_id': high_score.user_id,
            'username': username,
            'game': high_score.game,
            'game_name': high_score.game_name,
            'difficulty': high_score.difficulty,
            'score': high_score.score,
            'date': high_score.date,
            'message': high_score.message,
            'likes': high_score.likes,
            'user_likes_score': user_likes_score
        }
        high_scores_list.append(score_dict)
    
    all_games_scores = {}

    for score in high_scores_list:
        if score['game'] not in all_games_scores:
            all_games_scores[score['game']] = []
        all_games_scores[score['game']].append(score)

    sorted_games_scores = {}

    difficulties = ['easy', 'medium', 'hard']
    for game in games:
        if game.categories:
            for category in game.categories:
                category = category.lower().replace(' ', '').replace('&', '')
                if game.has_difficulty:
                    for difficulty in difficulties:
                        game_name = f"{game.param}_{category}_{difficulty}"
                        if game_name in all_games_scores:
                            sorted_games_scores[game_name] = all_games_scores[game_name]
                else:
                    game_name = f"{game.param}_{category}"
                    if game_name in all_games_scores:
                        sorted_games_scores[game_name] = all_games_scores[game_name]
        else:
            if game.has_difficulty:
                for difficulty in difficulties:
                    game_name = f"{game.param}_{difficulty}"
                    if game_name in all_games_scores:
                        sorted_games_scores[game_name] = all_games_scores[game_name]
            else:
                game_name = game.param
                if game_name in all_games_scores:
                    sorted_games_scores[game_name] = all_games_scores[game_name]

    return sorted_games_scores


def get_like_subquery(current_user_id):
    # Subquery to check if current user has liked a high score
    likes_subquery = db.session.query(scores_users).filter(
        scores_users.c.score_id == HighScore.id,
        scores_users.c.user_id == current_user_id
    ).exists().correlate(HighScore)
    return likes_subquery


def get_high_scores(game_name_param):

    current_user_id = current_user.id if current_user.is_authenticated else 0

    likes_subquery = get_like_subquery(current_user_id)

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
        HighScore.game == game_name_param
    ).order_by(
        HighScore.score.desc()
    )

    high_scores = high_scores_query.all()
    all_games_scores = organise_score_data(high_scores)
    return all_games_scores


def get_user_scores(username):

    current_user_id = current_user.id if current_user.is_authenticated else 0

    likes_subquery = get_like_subquery(current_user_id)

    user_id_subquery = db.session.query(User.id).filter(User.username == username).scalar_subquery()

    user_scores_query = db.session.query(
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
        HighScore.user_id == user_id_subquery
    ).order_by(
        HighScore.score.desc()
    )

    user_scores = user_scores_query.all()
    all_games_scores = organise_score_data(user_scores)
    return all_games_scores


def get_all_scores():

    current_user_id = current_user.id if current_user.is_authenticated else 0

    likes_subquery = get_like_subquery(current_user_id)

    all_scores_query = db.session.query(
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
    ).order_by(
        HighScore.score.desc()
    )

    all_scores = all_scores_query.all()
    all_games_scores = organise_score_data(all_scores)
    return all_games_scores

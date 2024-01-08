from flask import request
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from Games0App.models.high_score import HighScore, scores_users
from Games0App.games import games
from sqlalchemy.sql import case


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


def get_high_scores(game_name):

    current_user_id = current_user.id if current_user.is_authenticated else 0

    # Subquery to check if current user has liked a high score
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
    return high_scores

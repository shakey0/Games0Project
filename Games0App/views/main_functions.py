from flask import request, flash
from flask_login import current_user
from Games0App.extensions import redis_client
from Games0App.games import games
from Games0App.user_question_tracker import UserQuestionTracker
user_question_tracker = UserQuestionTracker()
import json
import random


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


def get_next_question(game, token, question_tracker, category_name, difficulty, first_question=False):

    formatted_category_name = game.format_category_name(category_name)

    if first_question and current_user.is_authenticated and game.load_route[0] != 'function':
        user_question_tracker.cache_questions(game.create_base_string(formatted_category_name, difficulty))

    count = 0
    while True:
        count += 1
        if count > 100:
            flash("Something went wrong.")
            # Log error here !!!!!!!!!!!!!
            return None
        next_question = game.get_question(question_tracker, category=category_name, difficulty=difficulty)
        print('NEXT QUESTION: ', next_question)
        if not next_question:
            flash("Something went wrong.")
            # Log error here !!!!!!!!!!!!!
            return None
        
        if current_user.is_authenticated and game.load_route[0] != 'function':
            result = user_question_tracker.deposit_question(
                game.create_base_string(formatted_category_name, difficulty), next_question['ID'])
            if result:
                break
        elif game.load_route[0] != 'function':
            result = user_question_tracker.deposit_question_unauth(
                game.create_base_string(formatted_category_name, difficulty), next_question['ID'], token)
            if result:
                break
        else:
            break
        question_tracker += 1

    redis_client.hset(token, 'question_tracker', next_question["last_question_no"])
    redis_client.hset(token, 'question', next_question["question"])
    redis_client.hset(token, 'answer', next_question["answer"])

    if "wrong_answers" in next_question:
        next_question["all_answers"] = [next_question["answer"]] + next_question["wrong_answers"]
        random.shuffle(next_question["all_answers"])
        redis_client.hset(token, 'all_answers', json.dumps(next_question["all_answers"]))
    
    return next_question


def confirm_all_questions_deposited(game, token, category_name, difficulty):

    if game.load_route[0] != 'function':
        formatted_category_name = game.format_category_name(category_name)
        game_string = game.create_base_string(formatted_category_name, difficulty)
        
        question_cache_key = token + "_unauth_question_cache_" + game_string
        cached_questions_ids = redis_client.lrange(question_cache_key, 0, -1)

        if cached_questions_ids:
            user_question_tracker.deposit_question_bundle(
                [id.decode('utf-8') for id in cached_questions_ids if id], game_string)

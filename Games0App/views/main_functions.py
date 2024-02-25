from flask import request, flash
from flask_login import current_user
from Games0App.extensions import redis_client
from Games0App.games import games
from Games0App.classes.user_question_tracker import user_question_tracker
from Games0App.classes.logger import Logger
logger = Logger()
import json
import random


def get_key_game_data(request_type):

    if request_type == 'GET':
        flash("Sorry! Either something went wrong, or you refreshed the page. Your game has expired. Please start a new game.", "error")
        return None

    token = request.form.get('token')

    game_type = redis_client.hget(token, 'game_type')
    if not game_type:
        flash("Sorry! Your game has expired. Please start a new game.", "error")
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
            error_type = 'unique_question_error'
            flash_message = "It is likely that there are a lack of questions for this game/category/difficulty combination."
            error_id = log_get_question_error(game, category_name, difficulty, error_type, flash_message)
            print('UNIQUE QUESTION ERROR: ', error_id)
            return None
        
        next_question = game.get_question(question_tracker, category=category_name, difficulty=difficulty)
        print('NEXT QUESTION: ', next_question)
        if not next_question:
            error_type = 'no_question_returned'
            flash_message = "An error occurred while retrieving your next question."
            error_id = log_get_question_error(game, category_name, difficulty, error_type, flash_message)
            print('NO QUESTION RETURNED: ', error_id)
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
    redis_client.hset(token, 'ID', next_question["ID"])

    if "wrong_answers" in next_question:
        next_question["all_answers"] = [next_question["answer"]] + next_question["wrong_answers"]
        random.shuffle(next_question["all_answers"])
        redis_client.hset(token, 'all_answers', json.dumps(next_question["all_answers"]))
    
    return next_question

def log_get_question_error(game, category_name, difficulty, error_type, flash_message):
    json_log = {
        'game_type': game.param,
        'category_name': category_name,
        'difficulty': difficulty
    }
    if current_user.is_authenticated:
        json_log['user_id'] = current_user.id
    unique_id = logger.log_event(json_log, 'get_next_question', error_type)
    flash("Sorry! Something went wrong!", "error")
    flash(flash_message, "error")
    flash("If you wish to contact me about this issue, please quote this case number: " + unique_id, "error")
    flash("I am also aware of the issue and will be looking into it.", "error")
    return unique_id


def confirm_all_questions_deposited(game, token, category_name, difficulty):

    if game.load_route[0] != 'function':
        formatted_category_name = game.format_category_name(category_name)
        game_string = game.create_base_string(formatted_category_name, difficulty)
        
        question_cache_key = token + "_unauth_question_cache_" + game_string
        cached_questions_ids = redis_client.lrange(question_cache_key, 0, -1)

        if cached_questions_ids:
            user_question_tracker.deposit_question_bundle(
                [id.decode('utf-8') for id in cached_questions_ids if id], game_string)

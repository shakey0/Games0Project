from flask import Blueprint, render_template, redirect, request, make_response, flash, jsonify
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.views.route_functions import get_key_game_data, get_next_question
from Games0App.utils import normalise_answer, is_close_match, find_and_convert_numbers, validate_victory_message
import secrets
import json
import random
import datetime


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', games=games, token=None, user=current_user)


@main.route('/game_setup')
def game_setup():

    game_type = request.args.get('game_type')
    if not game_type:
        return redirect('/')
    if request.args.get('category') == "All":
        game_type = game_type.replace('_categories', '')

    game = next(item for item in games if item.param == game_type)

    in_game = request.args.get('in_game')

    if game.categories:
        category = request.args.get('category')
        game_name = game.name + " - " + category if category else game.name
    else:
        game_name = game.name

    if game.categories and not in_game:
        in_game = "before"
        return render_template('game.html', in_game=in_game, categories=game.categories, game_type=game_type,
                                game_name=game_name, token=None, user=current_user)

    in_game = "intro"

    random_token = secrets.token_hex(16)
    token = f"{random_token}_{game_type}"
    redis_client.hset(token, 'game_type', game_type)
    redis_client.expire(token, 3600)

    if game.categories:
        redis_client.hset(token, 'category_name', category)
        redis_client.hset(token, 'category', category.lower().replace(' ', '').replace('&', ''))

    return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                            user=current_user)


@main.route('/game_play', methods=['GET', 'POST'])
def game_play():

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        print("GAME EXPIRED")
        flash("It looks like your game has expired.")
        return redirect('/')
    
    redis_client.hset(token, 'revealed_string', '')

    if request.form.get('in_game') == "start":

        if redis_client.hget(token, 'question_no'):  # Check if the game has already started and stop cheating
            flash("Either something went wrong, or you refreshed the page. Your game has expired.")
            return redirect('/')

        in_game = "yes"

        timer = int(request.form.get('speed'))
        redis_client.hset(token, 'timer', timer)

        difficulty = ""
        if game.has_difficulty:
            difficulty = request.form.get('difficulty')
            redis_client.hset(token, 'difficulty', difficulty)

        redis_client.hset(token, 'question_no', 1)
        
        cookied_question_number = request.cookies.get(game_name.lower().replace(' ', '_').replace('&', '_').replace('-', '_'))
        if cookied_question_number:
            cookied_question_number = int(cookied_question_number)
        else:
            cookied_question_number = 0
        print('COOKIED QUESTION NUMBER: ', cookied_question_number)

        next_question = get_next_question(game, token, cookied_question_number, category_name, difficulty)

        if "fill_blank" in game.param or "trivia_madness" in game.param:
            reveal_card_starter = 9
            length_card_starter = 5
            helpers = {'reveal_card': f"{reveal_card_starter} coupons",
            'length_card': f"{length_card_starter} coupons"}
            redis_client.hset(token, 'reveal_card', reveal_card_starter)
            redis_client.hset(token, 'length_card', length_card_starter)
        
        elif "_mc" in game.param:
            remove_higher_starter = 3
            remove_lower_starter = 3
            helpers = {'r_higher_card': f"{remove_higher_starter} coupons",
            'r_lower_card': f"{remove_lower_starter} coupons"}
            redis_client.hset(token, 'r_higher_card', remove_higher_starter)
            redis_client.hset(token, 'r_lower_card', remove_lower_starter)

        else:
            helpers = {}

        redis_client.hset(token, 'score', 0)

        response = make_response(render_template('game.html', in_game=in_game, game=game, token=token,
                                                game_name=game_name, next_question=next_question,
                                                question_no=1, timer=timer, score=0, user=current_user,
                                                helpers=helpers))
        response.set_cookie(game_name.lower().replace(' ', '_').replace('&', '_').replace('-', '_'),
                            str(next_question["last_question_no"]))
        
        return response if response else redirect('/')

    in_game = "yes"

    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))

    difficulty = ""
    if game.has_difficulty:
        difficulty = redis_client.hget(token, 'difficulty').decode('utf-8')

    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))
    if question_no != int(request.form.get('question_no')):
        flash("Either something went wrong, or you refreshed the page. Your game has expired.")
        return redirect('/')
    redis_client.hset(token, 'question_no', question_no+1)

    question_tracker = int(redis_client.hget(token, 'question_tracker').decode('utf-8'))

    next_question = get_next_question(game, token, question_tracker, category_name, difficulty)
    
    helpers = {}

    if "fill_blank" in game.param or "trivia_madness" in game.param:
        reveal_card = int(redis_client.hget(token, 'reveal_card').decode('utf-8'))
        helpers['reveal_card'] = f"{reveal_card} coupons" if reveal_card > 0 else "-60 points"
        length_card = int(redis_client.hget(token, 'length_card').decode('utf-8'))
        helpers['length_card'] = f"{length_card} coupons" if length_card > 0 else "-90 points"

    elif "_mc" in game.param:
        remove_higher = int(redis_client.hget(token, 'r_higher_card').decode('utf-8'))
        helpers['r_higher_card'] = f"{remove_higher} coupons" if remove_higher > 0 else "-90 points"
        remove_lower = int(redis_client.hget(token, 'r_lower_card').decode('utf-8'))
        helpers['r_lower_card'] = f"{remove_lower} coupons" if remove_lower > 0 else "-90 points"

    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    response = make_response(render_template('game.html', in_game=in_game, game=game, token=token,
                                            game_name=game_name, next_question=next_question,
                                            question_no=question_no+1, timer=timer, score=score,
                                            user=current_user, helpers=helpers))
    response.set_cookie(game_name.lower().replace(' ', '_').replace('&', '_').replace('-', '_'),
                        str(next_question["last_question_no"]))
        
    return response if response else redirect('/')


@main.route('/game_answer', methods=['GET', 'POST'])
def game_answer():

    in_game = "after"

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        print("GAME EXPIRED")
        flash("It looks like your game has expired.")
        return redirect('/')

    user_answer = request.form.get('answer')
    real_answer = redis_client.hget(token, 'answer').decode('utf-8')
    statement = False

    if user_answer and ("fill_blank" in game.param or "trivia_madness" in game.param):
        user_answer = find_and_convert_numbers(user_answer)
        correct = is_close_match(normalise_answer(user_answer), normalise_answer(real_answer))
        if (' and ' in user_answer or ' & ' in user_answer) and correct == False:
            answer_part_one = user_answer.split(' and ')[0].split(' & ')[0]
            answer_part_two = user_answer.split(' and ')[1].split(' & ')[1]
            user_answer = answer_part_two + ' and ' + answer_part_one
            correct = is_close_match(normalise_answer(user_answer), normalise_answer(real_answer))

    elif "number" in game.param:
        correct = user_answer == real_answer
        set_question = redis_client.hget(token, 'question').decode('utf-8')
        real_answer = f"{real_answer} = {set_question[39:-1]}"
        
    elif user_answer and "_mc" in game.param:
        correct = is_close_match(normalise_answer(user_answer), normalise_answer(real_answer))

    elif "_tf" in game.param:
        set_question = redis_client.hget(token, 'question').decode('utf-8')
        if user_answer == "True" and set_question == real_answer:
            correct, statement = True, True
        elif user_answer == "False" and set_question != real_answer:
            correct, statement = True, False
        elif user_answer == "True" and set_question != real_answer:
            correct, statement = False, False
        elif user_answer == "False" and set_question == real_answer:
            correct, statement = False, True
        else:
            correct, statement = False, set_question == real_answer

    else:
        user_answer = "No answer given"
        correct = False

    seconds_to_answer_left = int(request.form.get('countdown_timer'))
    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if correct:
        new_points = 100
        new_points += (seconds_to_answer_left + (60-timer)) * 5
        score += new_points
        redis_client.hset(token, 'score', score)
        seconds = timer - seconds_to_answer_left
    else:
        new_points = 0
        seconds = seconds_to_answer_left

    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))

    return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                            timer=timer, score=score, correct=correct, statement=statement, seconds=seconds,
                            new_points=new_points, question_no=question_no, real_answer=real_answer,
                            user=current_user)


@main.route('/game_finish', methods=['GET', 'POST'])
def game_finish():

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        print("GAME EXPIRED")
        flash("It looks like your game has expired.")
        return redirect('/')

    game_name_param = game.param
    if game.categories:
        category = redis_client.hget(token, 'category').decode('utf-8')
        game_name_param += "_" + category
    difficulty = redis_client.hget(token, 'difficulty').decode('utf-8') if "_mc" in game.param else ""
    if difficulty:
        game_name_param += "_" + difficulty
    redis_client.hset(token, 'game_name_param', game_name_param)

    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if current_user.is_authenticated:
        message = request.form.get('message')
        message_check = validate_victory_message(message)
        if message_check != True:
            return jsonify(success=False, error=message_check)
        high_score = HighScore(user_id=current_user.id, game=game_name_param, game_name=game_name,
                                difficulty=difficulty, score=score, date=datetime.datetime.now(),
                                message=message, likes=0)
        db.session.add(high_score)
        db.session.commit()
        redis_client.hset(token, 'high_score_saved', "yes")

    return jsonify(success=True, token=token)

from flask import Blueprint, render_template, redirect, request, make_response, flash
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.utils import normalise_answer, is_close_match, find_and_convert_numbers
import secrets
import json
import random
import datetime


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', games=games, user=current_user)


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
                                game_name=game_name, user=current_user)

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


def get_token_game_category_and_game_name():

    token = request.form.get('token')

    game_type = redis_client.hget(token, 'game_type').decode('utf-8')
    if not game_type:
        flash("Sorry, your game has expired. Please start again.")
        return redirect('/')
    game = next(item for item in games if item.param == game_type)

    category_name = ""
    if game.categories:
        category_name = redis_client.hget(token, 'category_name').decode('utf-8')
        game_name = game.name + " - " + category_name
    else:
        game_name = game.name
        
    return token, game, category_name, game_name


@main.route('/game_play', methods=['GET', 'POST'])
def game_play():

    if request.method == 'GET':
        flash("Either something went wrong, or you refreshed the page. Your game has expired.")
        return redirect('/')

    token, game, category_name, game_name = get_token_game_category_and_game_name()
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
        
        cookied_question_number = request.cookies.get(game_name.lower().replace(' ', '_').replace('&', '_').replace('-', '_'))
        if cookied_question_number:
            cookied_question_number = int(cookied_question_number)
        else:
            cookied_question_number = 0
        print('COOKIED QUESTION NUMBER: ', cookied_question_number)

        next_question = game.get_question(cookied_question_number, category=category_name, difficulty=difficulty)
        print('NEXT QUESTION: ', next_question)
        
        redis_client.hset(token, 'question_no', 1)
        redis_client.hset(token, 'question_tracker', next_question["last_question_no"])
        redis_client.hset(token, 'question', next_question["question"])
        redis_client.hset(token, 'answer', next_question["answer"])

        if len(next_question) == 4:
            next_question["all_answers"] = [next_question["answer"]] + next_question["wrong_answers"]
            random.shuffle(next_question["all_answers"])
            redis_client.hset(token, 'all_answers', json.dumps(next_question["all_answers"]))

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

    next_question = game.get_question(question_tracker, category=category_name, difficulty=difficulty)
    
    redis_client.hset(token, 'question_tracker', next_question["last_question_no"])
    redis_client.hset(token, 'question', next_question["question"])
    redis_client.hset(token, 'answer', next_question["answer"])

    if len(next_question) == 4:
        next_question["all_answers"] = [next_question["answer"]] + next_question["wrong_answers"]
        random.shuffle(next_question["all_answers"])
        redis_client.hset(token, 'all_answers', json.dumps(next_question["all_answers"]))
    
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

    if request.method == 'GET':
        flash("Either something went wrong, or you refreshed the page. Your game has expired.")
        return redirect('/')

    in_game = "after"

    token, game, category_name, game_name = get_token_game_category_and_game_name()

    answer = request.form.get('answer')
    real_answer = redis_client.hget(token, 'answer').decode('utf-8')
    statement = False
    if answer and ("fill_blank" in game.param or "trivia_madness" in game.param):
        answer = find_and_convert_numbers(answer)
        # TESTS FOR CONVERTING NUMBERS
        # - 1000000
        # - 48300894
        # - 1,000,000
        # - 32,059,320
        # - 100000
        # - 100,000
        # - 10000
        # - 10,000
        # - 1000
        # - 7,000
        # - 8,900
        # - 8900
        # - 1,000
        # - 100
        # - 10
        # - 1
        # - 5 million
        # - 96 thousand
        # - 2 hundred
        # - 1940
        # - 1800
        # - 1458
        # - and more...
        correct = is_close_match(normalise_answer(answer), normalise_answer(real_answer))

        # IMPORTANT TEST QUESTION:
        # What is the name for a group of gorillas?
        # Answer: band OR a band
        # test with single letter because this seemed to pass before

        # if correct == False and "fill_blank" in game.param and len(answer) <= 15:
        #     set_question = redis_client.hget(token, 'question').decode('utf-8')
        #     correct = check_blank_answer_for_alternative(answer.strip(), real_answer, set_question)
        #     if correct:
        #         real_answer = answer.strip()
        # elif correct == False and "trivia_madness" in game.param and len(answer) <= 25:
        #     pass
    elif "number" in game.param:
        correct = answer == real_answer
        set_question = redis_client.hget(token, 'question').decode('utf-8')
        real_answer = f"{real_answer} = {set_question[39:-1]}"
    elif answer and "_mc" in game.param:
        correct = is_close_match(normalise_answer(answer), normalise_answer(real_answer))
    elif "_tf" in game.param:
        set_question = redis_client.hget(token, 'question').decode('utf-8')
        if answer == "True" and set_question == real_answer:
            correct, statement = True, True
        elif answer == "False" and set_question != real_answer:
            correct, statement = True, False
        elif answer == "True" and set_question != real_answer:
            correct, statement = False, False
        elif answer == "False" and set_question == real_answer:
            correct, statement = False, True
        else:
            correct, statement = False, set_question == real_answer
    else:
        answer = "No answer given"
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

    if request.method == 'GET':
        flash("Either something went wrong, or you refreshed the page. Your game has expired.")
        return redirect('/')

    token, game, category_name, game_name = get_token_game_category_and_game_name()

    game_name_param = game.lower_name
    if game.categories:
        category = redis_client.hget(token, 'category').decode('utf-8')
        game_name_param += "_" + category
    difficulty = redis_client.hget(token, 'difficulty').decode('utf-8') if "_mc" in game.param else ""
    if difficulty:
        game_name_param += "_" + difficulty

    # timer = int(redis_client.hget(token, 'timer').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    # end_game_data = {"game_name": game_name_param, "score": score, "user_id": current_user.id}

    if current_user.is_authenticated:
        message = request.form.get('message')
        high_score = HighScore(user_id=current_user.id, game=game_name_param, score=score,
                                date=datetime.datetime.now(), message=message, likes=0)
        db.session.add(high_score)
        db.session.commit()

    return redirect(f'/scoreboard?token={token}')

from flask import Blueprint, render_template, redirect, request, make_response, jsonify, flash
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.mailjet_api import send_email
from Games0App.games import games
from Games0App.models.high_score import HighScore
from Games0App.models.answer_log import AnswerLog
from Games0App.views.main_functions import get_key_game_data, get_next_question, confirm_all_questions_deposited
from Games0App.classes.auth_token_manager import auth_token_manager
from Games0App.classes.auth_validator import auth_validator
from Games0App.classes.answer_checker import answer_checker
from Games0App.classes.logger import logger
from Games0App.utils import convert_scrambled_name
import os, secrets, datetime


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', games=games, token=None, user=current_user)


thanks = "Thank you for {} and visiting my website! It means a lot!"
recommendation = "For a quick and easy experience, I recommend trying one of the 'Trivia - Multiple Choice' quizzes. Enjoy!"

@main.route('/from_cv')
def index_from_cv():
    unique_id = logger.log_event({}, 'index_from_cv', 'from_cv')
    print('FROM CV: ' + unique_id)
    send_email(os.environ.get('MY_EMAIL_ADDRESS'), 'from_cv', 'cv_link')
    flash(thanks.format('reading my CV'), 'success')
    flash(recommendation, 'success')
    return redirect('/')

@main.route('/from_github_cv')
def index_from_github_cv():
    unique_id = logger.log_event({}, 'index_from_github_cv', 'from_github_cv')
    print('FROM GITHUB CV: ' + unique_id)
    send_email(os.environ.get('MY_EMAIL_ADDRESS'), 'from_github_cv', 'cv_link')
    flash(thanks.format('reading my GitHub CV'), 'success')
    flash(recommendation, 'success')
    return redirect('/')

@main.route('/from_github')
def index_from_github():
    unique_id = logger.log_event({}, 'index_from_github', 'from_github')
    print('FROM GITHUB: ' + unique_id)
    send_email(os.environ.get('MY_EMAIL_ADDRESS'), 'from_github', 'cv_link')
    flash(thanks.format('checking out this GitHub repository'), 'success')
    flash(recommendation, 'success')
    return redirect('/')

@main.route('/p/<scrambled_name>')
def index_p(scrambled_name):
    unscrambled_name = convert_scrambled_name(scrambled_name)
    unique_id = logger.log_event({}, 'index_p', unscrambled_name)
    print(f'From {unscrambled_name}: ' + unique_id)
    send_email(os.environ.get('MY_EMAIL_ADDRESS'), unscrambled_name, 'company_link')
    flash(f'Hello, {unscrambled_name}! Thank you for visiting my website! It means a lot!', 'success')
    flash(recommendation, 'success')
    return redirect('/')

@main.route('/t/<scrambled_name>')
def index_t(scrambled_name):
    unscrambled_name = convert_scrambled_name(scrambled_name)
    unique_id = logger.log_event({}, 'index_t', unscrambled_name)
    print(f'From {unscrambled_name}: ' + unique_id)
    flash(f'Hello, {unscrambled_name}! Thank you for visiting my website! It means a lot!', 'success')
    flash(recommendation, 'success')
    return redirect('/')


@main.route('/contact', methods=['POST'])
def contact():
    
    if not current_user.is_authenticated:
        return jsonify(success=False, error="Please log in to send me a message.")
    
    contact_message = request.form.get('contact_message')
    if not contact_message:
        return jsonify(success=False, error="Please type something!")
    if len(contact_message) < 50:
        return jsonify(success=False, error="Please type a little more.")
    if len(contact_message) > 500:
        return jsonify(success=False, error="Please keep your message under 500 characters.")
    
    if not auth_token_manager.attempt_check('send_contact_message', current_user.id):
        return jsonify(success=True, message="You've already sent me a message. Please wait a minute before sending another.")
    
    my_email = os.environ.get('MY_EMAIL_ADDRESS')
    send_email(my_email, current_user.username, 'contact', contact_message=contact_message, email_of_user=current_user.email)
    
    return jsonify(success=True, message="Your message has been sent. I'll get back to you as soon as I can.")


@main.route('/game_setup')
def game_setup():

    game_type = request.args.get('game_type')
    if not game_type:
        return redirect('/')
    if request.args.get('category') == "All":
        game_type = game_type.replace('_categories', '')

    in_game = request.args.get('in_game')

    difficulty = "medium"
    try:
        game = next(item for item in games if item.param == game_type)
    except StopIteration:
        if '_easy' in game_type or '_medium' in game_type or '_hard' in game_type:
            split_game_type = game_type.rsplit('_', 1)
            game_type = split_game_type[0]
            difficulty = split_game_type[1]
        if 'categories' in game_type:
            game_type = game_type.rsplit('_', 1)[0]
            in_game = "intro"
        game = next(item for item in games if item.param == game_type)

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
                            user=current_user, difficulty=difficulty)


@main.route('/game_play', methods=['GET', 'POST'])
def game_play():

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        return redirect('/')
    
    redis_client.hset(token, 'revealed_letter_string', '')

    if request.form.get('in_game') == "start" and not redis_client.hget(token, 'question_no'):

        redis_client.hset(token, 'question_no', 1)

        in_game = "yes"

        timer = int(request.form.get('speed'))
        redis_client.hset(token, 'timer', timer)

        difficulty = ""
        if game.has_difficulty:
            difficulty = request.form.get('difficulty')
            redis_client.hset(token, 'difficulty', difficulty)

        cookie_name = game.create_base_string(category_name, difficulty)
        cookied_question_number = request.cookies.get(cookie_name)
        if cookied_question_number:
            cookied_question_number = int(cookied_question_number)
        else:
            cookied_question_number = 0
        print('COOKIED QUESTION NUMBER:', cookied_question_number)

        next_question = get_next_question(game, token, cookied_question_number, category_name, difficulty,
                                            first_question=True)
        if not next_question:
            return redirect('/')

        if "fill_blank" in game.param or "trivia_madness" in game.param:
            reveal_letter_starter = 9
            reveal_length_starter = 5
            helpers = {'reveal_letter_card': f"{reveal_letter_starter} coupons",
                        'reveal_length_card': f"{reveal_length_starter} coupons"}
            redis_client.hset(token, 'reveal_letter_card', reveal_letter_starter)
            redis_client.hset(token, 'reveal_length_card', reveal_length_starter)
        
        elif "_mc" in game.param:
            remove_higher_starter = 3
            remove_lower_starter = 3
            helpers = {'remove_higher_card': f"{remove_higher_starter} coupons",
                        'remove_lower_card': f"{remove_lower_starter} coupons"}
            redis_client.hset(token, 'remove_higher_card', remove_higher_starter)
            redis_client.hset(token, 'remove_lower_card', remove_lower_starter)

        else:
            helpers = {}

        redis_client.hset(token, 'score', 0)

        response = make_response(render_template('game.html', in_game=in_game, game=game, token=token,
                                                game_name=game_name, next_question=next_question,
                                                question_no=1, timer=timer, score=0, user=current_user,
                                                helpers=helpers))
        response.set_cookie(cookie_name, str(next_question["last_question_no"]), max_age=3600)
        
        return response if response else redirect('/')
    
    elif request.form.get('in_game') == "start" and redis_client.hget(token, 'question_no'):
        log_duplicate_error(game_name, category_name, token, 'game_play', 'duplicate_question_request_start')
    
    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))
    if question_no == int(request.form.get('question_no')):
        redis_client.hset(token, 'question_no', question_no+1)
    else:
        log_duplicate_error(game_name, category_name, token, 'game_play', 'duplicate_question_request')

    in_game = "yes"

    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))

    difficulty = ""
    if game.has_difficulty:
        difficulty = redis_client.hget(token, 'difficulty').decode('utf-8')

    question_tracker = int(redis_client.hget(token, 'question_tracker').decode('utf-8'))

    next_question = get_next_question(game, token, question_tracker, category_name, difficulty)
    if not next_question:
        return redirect('/')
    
    helpers = {}

    if "fill_blank" in game.param or "trivia_madness" in game.param:
        reveal_letter = int(redis_client.hget(token, 'reveal_letter_card').decode('utf-8'))
        helpers['reveal_letter_card'] = f"{reveal_letter} coupons" if reveal_letter > 0 else "-60 points"
        reveal_length = int(redis_client.hget(token, 'reveal_length_card').decode('utf-8'))
        helpers['reveal_length_card'] = f"{reveal_length} coupons" if reveal_length > 0 else "-90 points"

    elif "_mc" in game.param:
        remove_higher = int(redis_client.hget(token, 'remove_higher_card').decode('utf-8'))
        helpers['remove_higher_card'] = f"{remove_higher} coupons" if remove_higher > 0 else "-90 points"
        remove_lower = int(redis_client.hget(token, 'remove_lower_card').decode('utf-8'))
        helpers['remove_lower_card'] = f"{remove_lower} coupons" if remove_lower > 0 else "-90 points"

    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    response = make_response(render_template('game.html', in_game=in_game, game=game, token=token,
                                            game_name=game_name, next_question=next_question,
                                            question_no=question_no+1, timer=timer, score=score,
                                            user=current_user, helpers=helpers))
    cookie_name = game.create_base_string(category_name, difficulty)
    response.set_cookie(cookie_name, str(next_question["last_question_no"]), max_age=3600)
        
    return response if response else redirect('/')


@main.route('/game_answer', methods=['GET', 'POST'])
def game_answer():

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        return redirect('/')
    
    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))
    if redis_client.hget(token, f'question_{question_no}'):
        repeat_request = True
        log_duplicate_error(game_name, category_name, token, 'game_answer', 'duplicate_answer_request')
    else:
        redis_client.hset(token, f'question_{question_no}', 'Completed')
        repeat_request = False

    in_game = "after"

    correct, statement, real_answer, user_answer = answer_checker.check_answer(token, game)

    seconds_to_answer_left = int(request.form.get('countdown_timer'))
    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if correct:
        new_points = 100
        new_points += (seconds_to_answer_left + (60-timer)) * 5
        if not repeat_request:
            score += new_points
            redis_client.hset(token, 'score', score)
        seconds = timer - seconds_to_answer_left
    else:
        new_points = 0
        seconds = seconds_to_answer_left
    
    if not repeat_request:
        difficulty = redis_client.hget(token, 'difficulty').decode('utf-8') if game.has_difficulty else ""
        question_id = redis_client.hget(token, 'ID').decode('utf-8')
        seconds_to_answer = timer - seconds_to_answer_left
        answer_log = AnswerLog(game_name=game_name, difficulty=difficulty, question_id=question_id,
                                real_answer=real_answer, user_answer=user_answer, correct=correct,
                                seconds_to_answer=seconds_to_answer, timestamp=datetime.datetime.now())
        db.session.add(answer_log)
        db.session.commit()

    return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                            timer=timer, score=score, correct=correct, statement=statement, seconds=seconds,
                            new_points=new_points, question_no=question_no, real_answer=real_answer,
                            user=current_user)


def log_duplicate_error(game_name, category_name, token, function, duplicate_request):
    user_id = current_user.id if current_user.is_authenticated else 0
    difficulty = redis_client.hget(token, 'difficulty')
    if difficulty:
        difficulty = difficulty.decode('utf-8')
    cached_question_no = redis_client.hget(token, 'question_no')
    if cached_question_no:
        cached_question_no = cached_question_no.decode('utf-8')
    request_question_no = request.form.get('question_no')
    json_log = {
        "user_id": user_id,
        "game_name": game_name,
        "category_name": category_name,
        "difficulty": difficulty,
        "cached_question_no": cached_question_no,
        "request_question_no": request_question_no
    }
    unique_id = logger.log_event(json_log, function, duplicate_request)
    print('DUPLICATE QUESTION REQUEST: ' + unique_id)


@main.route('/game_finish', methods=['GET', 'POST'])
def game_finish():

    try:
        token, game, category_name, game_name = get_key_game_data(request.method)
    except:
        return redirect('/')
    
    game_name_param = game.param
    if game.categories:
        category = redis_client.hget(token, 'category').decode('utf-8')
        game_name_param += "_" + category
    difficulty = redis_client.hget(token, 'difficulty').decode('utf-8') if "_mc" in game.param else ""
    if difficulty:
        game_name_param += "_" + difficulty
    redis_client.hset(token, 'game_name_param', game_name_param)

    if current_user.is_authenticated:

        score = int(redis_client.hget(token, 'score').decode('utf-8'))

        message_check = auth_validator.validate_victory_message()
        if message_check != True:
            return jsonify(success=False, error=message_check)
        
        high_score = HighScore(user_id=current_user.id, game=game_name_param, game_name=game_name,
                                difficulty=difficulty, category=category_name, score=score,
                                date=datetime.datetime.now(), message=request.form.get('message'), likes=0)
        db.session.add(high_score)
        db.session.commit()

        redis_client.hset(token, 'high_score_saved', "yes")

        confirm_all_questions_deposited(game, token, category_name, difficulty)

    return jsonify(success=True, token=token)

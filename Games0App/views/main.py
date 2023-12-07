from flask import Blueprint
from Games0App.extensions import db
from Games0App.models.user import User
from Games0App.classes import GamePlay, Category
from Games0App.utils import format_answer
from flask import render_template, request
import secrets
import os
import redis
production = os.environ.get('PRODUCTION', False)
if production:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)


main = Blueprint('main', __name__)


games = [
    GamePlay("Fill in the Blank - Facts",
            "You will be given 10 facts and need to fill in the blank word for each one.",
            param="fill_blank_facts", api_variable="facts"),
    GamePlay("Fill in the Blank - Jokes",
            "You will be given 10 jokes and need to fill in the blank word for each one.",
            param="fill_blank_jokes", api_variable="jokes"),
    GamePlay("Trivia Madness - Choose Your Category",
            "You will be given 10 questions from your chosen category.",
            param="trivia_madness", api_variable="trivia"),
    GamePlay("Countries & Cultures - Multiple Choice",
            "You will be given 10 questions about countries and cultures and need to select the correct answer for each one.",
            param="countries_cultures_mc"),
    GamePlay("Countries & Cultures - True or False",
            "You will be given 10 questions about countries and cultures and need to select whether each statement is true or false.",
            param="countries_cultures_tf"),
    GamePlay("Number to Reach",
            "DIFFERENT MESSAGE",
            param="number_to_reach")
]


@main.route('/')
def index():
    return render_template('index.html', games=games)


@main.route('/game_setup')
def game_setup():

    game_type = request.args.get('game_type')
    game = next(item for item in games if item.param == game_type)

    in_game = request.args.get('in_game')

    if game_type == 'trivia_madness' and not in_game:
        in_game = "before"
        categories = [Category("Art & Literature"), Category("Language"), Category("Science & Nature"),
            Category("General"), Category("Food & Drink"), Category("People & Places"),
            Category("Geography"), Category("History & Holidays"), Category("Entertainment"),
            Category("Toys & Games"), Category("Music"), Category("Mathematics"),
            Category("Religion & Mythology"), Category("Sports & Leisure")]
        return render_template('game_setup.html', in_game=in_game, categories=categories, game_type=game_type)
    else:
        in_game = "intro"

        # LOGIC FOR IF USER IS AUTHENTICATED
        # if current_user.is_authenticated:

        random_token = secrets.token_hex(16)
        token = f"{random_token}_{game_type}"
        redis_client.hset(token, 'game_type', game_type)
        redis_client.expire(token, 3600)

        if game_type == "trivia_madness":
            category = request.args.get('category')
            redis_client.hset(token, 'category', category.lower().replace(' ', '').replace('&', ''))
            game_name = "Trivia Madness - " + category
        else:
            game_name = game.name
        return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name)


@main.route('/game_play', methods=['POST'])
def game_play():

    token = request.form.get('token')
    game_type = redis_client.hget(token, 'game_type').decode('utf-8')
    if not game_type:
        # FLASH A MESSAGE HERE TO SAY THE GAME HAS EXPIRED
        return render_template('index.html', games=games)
    game = next(item for item in games if item.param == game_type)

    if game_type == "trivia_madness":
        category = redis_client.hget(token, 'category').decode('utf-8')
        game_name = "Trivia Madness - " + category
    else:
        game_name = game.name

    if request.form.get('in_game') == "start":

        in_game = "yes"

        timer = int(request.form.get('difficulty'))
        redis_client.hset(token, 'timer', timer)
        # GET QUESTION FROM CLASS
        next_question = (55, "Question from Redis")  # game.get_question(0)
        redis_client.hset(token, 'question_no', 1)
        redis_client.hset(token, 'question_tracker', next_question[0])
        redis_client.hset(token, 'question', next_question[1])
        redis_client.hset(token, 'score', 0)

        return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                                next_question=next_question, question_no=1, timer=timer, score=0)

    in_game = "yes"

    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))

    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))
    redis_client.hset(token, 'question_no', question_no+1)

    question_tracker = int(redis_client.hget(token, 'question_tracker').decode('utf-8'))
    last_question = redis_client.hget(token, 'question').decode('utf-8')

    # GET QUESTION FROM CLASS
    next_question = (55, "Question from Redis")
    redis_client.hset(token, 'question_tracker', next_question[0])
    redis_client.hset(token, 'question', next_question[1])

    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                            next_question=next_question, question_no=question_no+1, timer=timer,
                            score=score)


@main.route('/game_answer', methods=['POST'])
def game_answer():

    in_game = "after"

    token = request.form.get('token')
    game_type = redis_client.hget(token, 'game_type').decode('utf-8')
    if not game_type:
        # FLASH A MESSAGE HERE TO SAY THE GAME HAS EXPIRED
        return render_template('index.html', games=games)
    game = next(item for item in games if item.param == game_type)

    if game_type == "trivia_madness":
        category = redis_client.hget(token, 'category').decode('utf-8')
        game_name = "Trivia Madness - " + category
    else:
        game_name = game.name

    answer = request.form.get('answer')
    question_tracker = int(redis_client.hget(token, 'question_tracker').decode('utf-8'))
    # real_answer = game_play.get_answer(question_tracker, AND......(if category:))
    real_answer = "Answer from Redis"
    correct = True if format_answer(answer) == format_answer(real_answer) else False

    seconds_to_answer_left = int(request.form.get('countdown_timer'))
    timer = int(redis_client.hget(token, 'timer').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if correct:
        new_points = 100
        new_points += (seconds_to_answer_left + (30-timer)) * 10
        score += new_points
        redis_client.hset(token, 'score', score)
        seconds = timer - seconds_to_answer_left
    else:
        new_points = 0
        seconds = seconds_to_answer_left

    question_no = int(redis_client.hget(token, 'question_no').decode('utf-8'))

    return render_template('game.html', in_game=in_game, game=game, token=token, game_name=game_name,
                            timer=timer, score=score, correct=correct, seconds=seconds,
                            new_points=new_points, question_no=question_no)


# @main.route('/game', methods=['GET', 'POST'])
# def game():

#     game_type = request.args.get('game_type')
#     game_play = next(game for game in games if game.param == game_type)

#     in_game = request.args.get('in_game')

#     if game_type == 'trivia_madness' and not in_game:
#         in_game = "before"
#         categories = [Category("Art & Literature"), Category("Language"), Category("Science & Nature"),
#             Category("General"), Category("Food & Drink"), Category("People & Places"),
#             Category("Geography"), Category("History & Holidays"), Category("Entertainment"),
#             Category("Toys & Games"), Category("Music"), Category("Mathematics"),
#             Category("Religion & Mythology"), Category("Sports & Leisure")]
#         return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type)
#     else:
#         categories = []

#     category = ""
#     game_name = game_play.name

#     if game_type == "trivia_madness":
#         category = request.args.get('category')
#         game_name = "Trivia Madness - " + category

#     elif not in_game:
#         in_game = "intro"
#         return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type,
#                                 game=game_play, game_name=game_name, score=0)

#     score = 0
#     timer = 0
#     question_no = 0
#     next_question = ()

#     if in_game == "yes":

#         timer = int(request.args.get('difficulty'))

#         question_no = int(request.args.get('question_no'))
#         question_no += 1

#         question_tracker = request.args.get('question_tracker')
#         if not question_tracker:
#             question_tracker = 0
#         next_question = game_play.get_question(question_tracker, category)

#         score = int(request.args.get('score'))
    
#     seconds = 0
#     new_points = 0
#     correct = False

#     if in_game == "after":

#         timer = int(request.args.get('difficulty'))
        
#         question_no = int(request.args.get('question_no'))

#         question_tracker = request.args.get('question_tracker')
#         answer = request.args.get('answer')
#         real_answer = game_play.get_answer(question_tracker)
#         correct = True if format_answer(answer) == format_answer(real_answer) else False

#         score = int(request.args.get('score'))
#         seconds_to_answer_left = int(request.args.get('countdown_timer'))
#         if correct:
#             new_points = 100
#             new_points += (30 - seconds_to_answer_left) * 10
#             score += new_points
#             seconds = timer - seconds_to_answer_left
#         else:
#             seconds = seconds_to_answer_left

#     if in_game == "finish":

#         timer = int(request.args.get('difficulty'))

#         score = int(request.args.get('score'))

#         return render_template('scoreboard.html', timer=timer, score=score, game_name=game_name,
#                                 game_type=game_type, category=category, game=game_play)


#     return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type,
#                             game=game_play, timer=timer, category=category, game_name=game_name,
#                             question_no=question_no, next_question=next_question, correct=correct,
#                             score=score, seconds=seconds, new_points=new_points)







"""
[
  {
    "category": "historyholidays",
    "question": "Three of the names of Santa's reindeer begin with the letter 'D'', name two of them ",
    "answer": "Dancer, Dasher, Donner"
  },
    {
    "category": "historyholidays",
    "question": "What pope died 33 days after his election ",
    "answer": "John Paul i"
  }
]
"""
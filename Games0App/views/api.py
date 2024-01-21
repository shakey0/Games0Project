from flask import Blueprint, request, jsonify
from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.high_score import HighScore, scores_users
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError
import json
import random


api = Blueprint('api', __name__)


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


@api.route('/reveal_letter', methods=['POST'])
def reveal_letter():

    token = request.form.get('token')

    reveal_card = int(redis_client.hget(token, 'reveal_card').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if reveal_card == 0:
        if score < 60:
            return jsonify(success=False, message='You need at least 60 points to reveal a letter!')
    
    revealed_string = redis_client.hget(token, 'revealed_string').decode('utf-8')

    answer = redis_client.hget(token, 'answer').decode('utf-8')

    answer = answer.strip()
    for article in ['the ', 'a ', 'an ']:
        if answer.lower().startswith(article):
            answer = answer[len(article):]
            break

    answer = answer.replace(' ', '').replace('-', '').replace('&', '').replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '').replace(':', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '')

    alphanumeric_positions = [i for i, char in enumerate(answer) if char.isalnum()]
    count = 0
    random_position = -1
    while count < 100:
        count += 1
        random_position = random.choice(alphanumeric_positions)
        if not str(random_position) in revealed_string:
            revealed_string += str(random_position)
            redis_client.hset(token, 'revealed_string', revealed_string)
            break
        random_position = -1
    if random_position == -1:
        return jsonify(success=False, message='No more letters to reveal!')
    random_char = answer[random_position]

    message =  f"The {ordinal(random_position + 1)} character is {random_char}."

    if reveal_card > 0:
        reveal_card -= 1
        redis_client.hset(token, 'reveal_card', reveal_card)
        reveal_card_text = f"{reveal_card} coupons" if reveal_card > 0 else "-60 points"
    else:
        score -= 60
        redis_client.hset(token, 'score', score)
        reveal_card_text = "-60 points"

    return jsonify(success=True, score=score, message=message, reveal_card_text=reveal_card_text)


@api.route('/reveal_length', methods=['POST'])
def reveal_length():

    token = request.form.get('token')

    length_card = int(redis_client.hget(token, 'length_card').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if length_card == 0:
        if score < 90:
            return jsonify(success=False, message='You need at least 90 points to reveal the length of the answer!')

    answer = redis_client.hget(token, 'answer').decode('utf-8')

    answer = answer.lower().strip()
    # for article in ['the ', 'a ', 'an ']:
    #     if answer.startswith(article):
    #         answer = answer[len(article):]
    #         break

    answer = answer.replace('-', ' ').replace('&', '').replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '').replace(':', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '')

    no_of_words = len(answer.split())
    if no_of_words == 1:
        message = f"The answer is {len(answer)} letters."
    else:
        word_lengths = [len(word) for word in answer.split()]
        message = f"The word lengths are {', '.join([str(length) for length in word_lengths[:-1]])} and {word_lengths[-1]} letters respectively."

    if length_card > 0:
        length_card -= 1
        redis_client.hset(token, 'length_card', length_card)
        length_card_text = f"{length_card} coupons" if length_card > 0 else "-90 points"
    else:
        score -= 90
        redis_client.hset(token, 'score', score)
        length_card_text = "-90 points"

    return jsonify(success=True, score=score, message=message, length_card_text=length_card_text)


@api.route('/remove_higher', methods=['POST'])
def remove_higher():

    token = request.form.get('token')

    higher_card = int(redis_client.hget(token, 'r_higher_card').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if higher_card == 0:
        if score < 90:
            return jsonify(success=False, message='You need at least 90 points to remove a wrong answer!')
        
    answer = redis_client.hget(token, 'answer').decode('utf-8')
    all_answers = json.loads(redis_client.hget(token, 'all_answers').decode('utf-8'))

    if all_answers[0] == answer:
        answer_to_remove = all_answers[1]
    elif all_answers[1] == answer:
        answer_to_remove = all_answers[0]
    else:
        random_pick = random.randint(0, 1)
        answer_to_remove = all_answers[random_pick]
    
    if higher_card > 0:
        higher_card -= 1
        redis_client.hset(token, 'r_higher_card', higher_card)
        higher_card_text = f"{higher_card} coupons" if higher_card > 0 else "-90 points"
    else:
        score -= 90
        redis_client.hset(token, 'score', score)
        higher_card_text = "-90 points"

    return jsonify(success=True, score=score, answer_to_remove=answer_to_remove, higher_card_text=higher_card_text)


@api.route('/remove_lower', methods=['POST'])
def remove_lower():

    token = request.form.get('token')

    lower_card = int(redis_client.hget(token, 'r_lower_card').decode('utf-8'))
    score = int(redis_client.hget(token, 'score').decode('utf-8'))

    if lower_card == 0:
        if score < 90:
            return jsonify(success=False, message='You need at least 90 points to remove a wrong answer!')
        
    answer = redis_client.hget(token, 'answer').decode('utf-8')
    all_answers = json.loads(redis_client.hget(token, 'all_answers').decode('utf-8'))

    if all_answers[2] == answer:
        answer_to_remove = all_answers[3]
    elif all_answers[3] == answer:
        answer_to_remove = all_answers[2]
    else:
        random_pick = random.randint(2, 3)
        answer_to_remove = all_answers[random_pick]
    
    if lower_card > 0:
        lower_card -= 1
        redis_client.hset(token, 'r_lower_card', lower_card)
        lower_card_text = f"{lower_card} coupons" if lower_card > 0 else "-90 points"
    else:
        score -= 90
        redis_client.hset(token, 'score', score)
        lower_card_text = "-90 points"

    return jsonify(success=True, score=score, answer_to_remove=answer_to_remove, lower_card_text=lower_card_text)


@api.route('/like_high_score', methods=['POST'])
def like_high_score():

    if not current_user.is_authenticated:
        return jsonify(success=False, error="Something wasn't right there...")
    
    score_id = request.form['score_id']
    liked = True if request.form['liked'] == "yes" else False

    try:
        with db.session.begin_nested():

            update_statement = (
                update(HighScore)
                .where(HighScore.id == score_id)
                .values(likes=HighScore.likes - 1 if liked else HighScore.likes + 1)
                .returning(HighScore.likes)
            )
            new_likes_count = db.session.execute(update_statement).scalar()

            if liked:
                delete_statement = (
                    delete(scores_users)
                    .where(scores_users.c.score_id == score_id)
                    .where(scores_users.c.user_id == current_user.id)
                )
                db.session.execute(delete_statement)
            else:
                insert_statement = (
                    scores_users.insert()
                    .values(score_id=score_id, user_id=current_user.id)
                )
                db.session.execute(insert_statement)

        db.session.commit()

    except IntegrityError as e:
        print(f"Integrity Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")

    if new_likes_count is not None:
        return jsonify(success=True, newLikesCount=new_likes_count)
    else:
        return jsonify(success=False, error="Something wasn't right there...")

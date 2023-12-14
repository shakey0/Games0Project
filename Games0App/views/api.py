from flask import Blueprint, request, jsonify
import os
import redis
production = os.environ.get('PRODUCTION', False)
if production:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)
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

    answer = answer.lower().strip()
    for article in ['the ', 'a ', 'an ']:
        if answer.startswith(article):
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

    message =  f"The {ordinal(random_position + 1)} character is {random_char}"

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
    for article in ['the ', 'a ', 'an ']:
        if answer.startswith(article):
            answer = answer[len(article):]
            break

    answer = answer.replace('-', ' ').replace('&', '').replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '').replace(':', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '')

    if answer.isnumeric() and len(answer) == 1:
        digit_to_word = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three',
            '4': 'four', '5': 'five', '6': 'six', '7': 'seven',
            '8': 'eight', '9': 'nine'
        }
        answer = digit_to_word[answer]

    no_of_words = len(answer.split())
    no_of_words_part = "a single word" if no_of_words == 1 else f"{no_of_words} words"

    message = f"The answer is {no_of_words_part} totalling {len(answer.replace(' ', ''))} characters."

    if length_card > 0:
        length_card -= 1
        redis_client.hset(token, 'length_card', length_card)
        length_card_text = f"{length_card} coupons" if length_card > 0 else "-90 points"
    else:
        score -= 90
        redis_client.hset(token, 'score', score)
        length_card_text = "-90 points"

    return jsonify(success=True, score=score, message=message, length_card_text=length_card_text)

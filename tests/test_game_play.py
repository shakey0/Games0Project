from unittest.mock import patch
from Games0App.extensions import redis_client
from Games0App.classes.game_play import GamePlay
from Games0App.models.log import Log
import json

def test_init_game_play(test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'test_file']
    )
    assert game.name == "Test - Game"
    assert game.lower_name == "testgame"
    assert game.image == "testgame.png"
    assert game.intro_message == "Welcome to this game!"
    assert game.param == "test_param"
    assert game.load_route == ['csv', 'test_file']
    assert game.default == True
    assert game.categories == []
    assert game.has_difficulty == False
    assert game.question_numbers == {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
                                    6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}
    
    game2 = GamePlay(
        name="Test - Game 2",
        intro_message="Welcome to this game!",
        param="test_param_categories",
        load_route=['csv', 'test_file'],
        categories=["Category 1", "Category 2"],
        has_difficulty=True
    )
    assert game2.name == "Test - Game 2"
    assert game2.lower_name == "testgame2"
    assert game2.image == "testgame2.png"
    assert game2.param == "test_param_categories"
    assert game2.default == True
    assert game2.categories == ["Category 1", "Category 2"]
    assert game2.has_difficulty == True
    
    game3 = GamePlay(
        name="Test - Game 2",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'test_file'],
        default=False,
        has_difficulty=True
    )
    assert game3.default == False
    assert game.categories == []
    assert game3.has_difficulty == True

def test_get_questions_from_api(test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['api', 'https://the-trivia-api.com/api/questions?limit=50&categories={}&difficulty={}'],
        categories=["Music", "Sport & Leisure"],
        has_difficulty=True
    )
    result = game.get_questions_from_api("sport_and_leisure", "easy")
    assert all(question['category'] == "Sport & Leisure" for question in result)
    assert all(question['difficulty'] == "easy" for question in result)
    assert all(question['type'] == "Multiple Choice" for question in result)
    assert all(question['correctAnswer'] for question in result)
    assert all(len(question['incorrectAnswers']) == 3 for question in result)
    assert all(question['question'] for question in result)

@patch('Games0App.classes.game_play.current_user')
def test_log_api_error(mock_current_user, test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['api', 'https://the-trivia-api.com/api/questionz?limit=50&categories={}&difficulty={}'],
        categories=["Music", "Sport & Leisure"],
        has_difficulty=True
    )
    mock_current_user.id = None
    game.get_questions_from_api("music", "easy")
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].user_id == None
    assert logs[0].function_name == "get_questions_from_api"
    assert logs[0].log_type == "api_error"
    assert logs[0].data['error_type'] == 'BadStatusCode'
    assert logs[0].data['url'] == 'https://the-trivia-api.com/api/questionz?limit=50&categories=music&difficulty=easy'

    

def test_get_questions_from_csv(test_app):
    
    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'trivia_madness'],
        categories=["Science & Nature", "Science - HARD", "Art & Literature - HARD"]
    )
    result = game.get_questions_from_csv("art_and_literature", "")
    assert len(result) == 30
    assert all(question['category'] == "art_literature" for question in result)
    assert all(question['ID'] for question in result)
    assert all(question['question'] for question in result)
    assert all(question['answer'] for question in result)

    game2 = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'true_or_false_trivia']
    )
    result2 = game2.get_questions_from_csv("", "")
    assert len(result2) == 30
    assert all(question['category'] in ["animals", "countries", "cities", "food"] for question in result2)
    assert all(question['ID'] for question in result2)
    assert all(question['statement'] for question in result2)
    assert all(question['answer'] for question in result2)
    for question in result2:
        if len(question['options']) != 2:
            print(question)
    assert all(len(question['options']) == 2 for question in result2)

def test_get_questions_from_function(test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['function', 'sum_generator']
    )
    result = game.get_questions_from_function("", "medium")
    assert len(result) == 30
    assert all(len(question) == 4 for question in result)
    assert all(question[0] == 0 for question in result)
    assert all(len(question[3]) == 3 for question in result)

questions_as_lists = [
    ['24', 'Which British monarch popularised the Christmas tree in the UK?', 'Queen Victoria'],
    ['302', 'What is the name of the first book in the Bible?', 'Genesis'],
    ['131', 'What is the capital of Australia?', 'Canberra']
]
questions_as_dicts = [
    {'ID': '24', 'question': 'Which British monarch popularised the Christmas tree in the UK?', 'answer': 'Queen Victoria'},
    {'ID': '302', 'question': 'What is the name of the first book in the Bible?', 'answer': 'Genesis'},
    {'ID': '131', 'question': 'What is the capital of Australia?', 'answer': 'Canberra'}
]
questions_as_lists_mc = [
    ['24', 'Which British monarch popularised the Christmas tree in the UK?', 'Queen Victoria', ['King George', 'King Edward', 'King Henry']],
    ['302', 'What is the name of the first book in the Bible?', 'Genesis', ['Exodus', 'Leviticus', 'Numbers']],
    ['131', 'What is the capital of Australia?', 'Canberra', ['Sydney', 'Melbourne', 'Brisbane']]
]
questions_as_dicts_mc = [
    {'ID': '24', 'question': 'Which British monarch popularised the Christmas tree in the UK?', 'answer': 'Queen Victoria', 'wrong_answers': ['King George', 'King Edward', 'King Henry']},
    {'ID': '302', 'question': 'What is the name of the first book in the Bible?', 'answer': 'Genesis', 'wrong_answers': ['Exodus', 'Leviticus', 'Numbers']},
    {'ID': '131', 'question': 'What is the capital of Australia?', 'answer': 'Canberra', 'wrong_answers': ['Sydney', 'Melbourne', 'Brisbane']}
]
def test_update_stored_questions(test_app):
    
    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'trivia_madness']
    )
    redis_client.flushall()
    assert game.update_stored_questions(questions_as_lists, 'test_group') == True
    assert game.update_stored_questions([], 'test_group_2') == False
    questions = redis_client.smembers('test_group')
    questions = [json.loads(question.decode('utf-8')) for question in questions]
    assert len(questions) == 3
    assert all(question in questions_as_lists for question in questions)

def test_get_question_from_redis_set(test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'trivia_madness']
    )
    redis_client.flushall()
    game.update_stored_questions(questions_as_lists, 'testgame_collection')
    result = game.get_question_from_redis_set('testgame_collection', '', '')
    assert 'last_question_no' in result
    result.pop('last_question_no')
    assert result in questions_as_dicts
    assert redis_client.get('testgame_last_question_no').decode('utf-8') == '1'
    assert json.loads(redis_client.hget('testgame_hash', 'testgame_1').decode('utf-8')) in questions_as_lists
    result = game.get_question_from_redis(0, 'testgame_1', '', '')
    assert 'last_question_no' in result
    result.pop('last_question_no')
    assert result in questions_as_dicts

    game2 = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'https://the-trivia-api.com/api/questions?limit=50&categories={}&difficulty={}'],
        categories=["Music", "Sport & Leisure"],
        has_difficulty=True
    )
    redis_client.flushall()
    game.update_stored_questions(questions_as_lists_mc, 'testgame_music_easy_collection')
    game2.get_question_from_redis_set('testgame_music_easy_collection', 'music', 'easy')
    game2.get_question_from_redis_set('testgame_music_easy_collection', 'music', 'easy')
    result2 = game2.get_question_from_redis_set('testgame_music_easy_collection', 'music', 'easy')
    assert 'last_question_no' in result2
    result2.pop('last_question_no')
    assert result2 in questions_as_dicts_mc
    assert redis_client.get('testgame_music_easy_last_question_no').decode('utf-8') == '3'
    assert json.loads(redis_client.hget('testgame_music_easy_hash', 'testgame_music_easy_3').decode('utf-8')) in questions_as_lists_mc
    result2 = game2.get_question_from_redis(0, 'testgame_music_easy_3', 'music', 'easy')
    assert 'last_question_no' in result2
    result2.pop('last_question_no')
    assert result2 in questions_as_dicts_mc

def test_get_question(test_app):

    game = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['csv', 'jokes']
    )
    redis_client.flushall()
    question = game.get_question(5, '', '')
    assert 'last_question_no' in question
    assert question['last_question_no'] == 1
    assert 'ID' in question
    assert 'question' in question
    assert 'answer' in question
    collection = redis_client.smembers('testgame_collection')
    collection = [json.loads(question.decode('utf-8')) for question in collection]
    assert all(len(question) == 3 for question in collection)
    assert all('____' in question[1] for question in collection)
    hash = redis_client.hgetall('testgame_hash')
    hash = {key.decode('utf-8'): json.loads(value.decode('utf-8')) for key, value in hash.items()}
    assert 'testgame_1' in hash
    assert len(hash['testgame_1']) == 3
    assert redis_client.get('testgame_last_question_no').decode('utf-8') == '1'
    game.get_question(2, '', '')
    question = game.get_question(3, '', '')
    assert question['last_question_no'] == 3
    assert redis_client.get('testgame_last_question_no').decode('utf-8') == '3'
    question = game.get_question(11, '', '')
    assert question['last_question_no'] == 4
    assert redis_client.get('testgame_last_question_no').decode('utf-8') == '4'

    game2 = GamePlay(
        name="Test - Game",
        intro_message="Welcome to this game!",
        param="test_param",
        load_route=['api', 'https://the-trivia-api.com/api/questions?limit=50&categories={}&difficulty={}'],
        categories=["Music", "Sport & Leisure"],
        has_difficulty=True
    )
    redis_client.flushall()
    question = game2.get_question(5, 'music', 'easy')
    assert 'last_question_no' in question
    assert question['last_question_no'] == 1
    assert 'ID' in question
    assert 'question' in question
    assert 'answer' in question
    assert len(question['wrong_answers']) == 3
    collection = redis_client.smembers('testgame_music_easy_collection')
    collection = [json.loads(question.decode('utf-8')) for question in collection]
    assert all(len(question) == 4 for question in collection)
    hash = redis_client.hgetall('testgame_music_easy_hash')
    hash = {key.decode('utf-8'): json.loads(value.decode('utf-8')) for key, value in hash.items()}
    assert 'testgame_music_easy_1' in hash
    assert len(hash['testgame_music_easy_1']) == 4
    assert redis_client.get('testgame_music_easy_last_question_no').decode('utf-8') == '1'
    game2.get_question(2, 'music', 'easy')
    question = game2.get_question(3, 'music', 'easy')
    assert question['last_question_no'] == 3
    assert redis_client.get('testgame_music_easy_last_question_no').decode('utf-8') == '3'
    question = game2.get_question(11, 'music', 'easy')
    assert question['last_question_no'] == 4
    assert redis_client.get('testgame_music_easy_last_question_no').decode('utf-8') == '4'

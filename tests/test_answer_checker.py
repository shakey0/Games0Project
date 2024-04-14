from unittest.mock import patch, MagicMock
from Games0App.extensions import redis_client
from Games0App.games import games
from Games0App.classes.answer_checker import answer_checker
import secrets


def test_normalise_answer():
    assert answer_checker.normalise_answer("Hello World") == "helloworld", "Failed to convert to lowercase or remove space"
    assert answer_checker.normalise_answer("  Hello  ") == "hello", "Failed to strip spaces"
    assert answer_checker.normalise_answer("Rock & Roll") == "rockroll", "Failed to replace '&'"
    assert answer_checker.normalise_answer("Bread and Butter") == "breadbutter", "Failed to replace 'and'"
    assert answer_checker.normalise_answer("The Beatles") == "beatles", "Failed to remove 'the '"
    assert answer_checker.normalise_answer("A Day to Remember") == "daytoremember", "Failed to remove 'a '"
    assert answer_checker.normalise_answer("An Apple") == "apple", "Failed to remove 'an '"
    assert answer_checker.normalise_answer("Some Girls") == "girls", "Failed to remove 'some '"
    assert answer_checker.normalise_answer("Hello, World!") == "helloworld", "Failed to remove punctuation"
    assert answer_checker.normalise_answer("He's a Hero") == "hero", "Failed complex case: 'He's a '"
    assert answer_checker.normalise_answer("Phase 3 - Step #2") == "phase3step2", "Failed to remove symbols or process numbers"
    assert answer_checker.normalise_answer("It's the Great Pumpkin, Charlie Brown") == "greatpumpkincharliebrown", "Failed with multiple noise words"
    assert answer_checker.normalise_answer("They're going to the park") == "goingtothepark", "Failed with compound noise words and conjunctions"
    assert answer_checker.normalise_answer("Star Wars: Episode IV - 'A New Hope'") == "starwarsepisodeivanewhope", "Failed with quotes and colons"
    assert answer_checker.normalise_answer("Café & Crêperie") == "cafécrêperie", "Failed with non-ASCII characters"
    assert answer_checker.normalise_answer("THIS IS A TEST") == "thisisatest", "Failed with all uppercase input"
    assert answer_checker.normalise_answer("simpletest") == "simpletest", "Failed with simple input with no changes"
    assert answer_checker.normalise_answer("MixEd CaSe Input") == "mixedcaseinput", "Failed with mixed case and spacing"
    assert answer_checker.normalise_answer("Well, this is something; quite complex! Isn't it?") == "wellthisissomethingquitecomplexisntit", "Failed removing multiple punctuation types"


def test_is_close_match():
    assert answer_checker.is_close_match('answer', 'answer') == True
    assert answer_checker.is_close_match('anser', 'answer') == True
    assert answer_checker.is_close_match('answer', 'anser') == True
    assert answer_checker.is_close_match('answet', 'answer') == True
    assert answer_checker.is_close_match('answrt', 'answer') == True
    assert answer_checker.is_close_match('answft', 'answer') == False
    assert answer_checker.is_close_match('answer', 'answre') == True
    assert answer_checker.is_close_match('answre', 'answer') == True
    assert answer_checker.is_close_match('nswera', 'answer') == True
    assert answer_checker.is_close_match('snwera', 'answer') == False
    assert answer_checker.is_close_match('extraanswer', 'answer') == True
    assert answer_checker.is_close_match('answer', 'extraanswer') == False
    assert answer_checker.is_close_match('extraanser', 'answer') == True
    assert answer_checker.is_close_match('extraanswer', 'anser') == True
    assert answer_checker.is_close_match('extraanswrt', 'answer') == True
    assert answer_checker.is_close_match('extraanswft', 'answer') == False
    assert answer_checker.is_close_match('extraanswer', 'answre') == True
    assert answer_checker.is_close_match('extraanswre', 'answer') == True
    assert answer_checker.is_close_match('extranswera', 'answer') == True
    assert answer_checker.is_close_match('extrasnwera', 'answer') == False


def test_check_answer_type_in_answer(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_fill_blank_facts"
    redis_client.hset(token, 'game_type', "fill_blank_facts")
    redis_client.expire(token, 5)
    
    redis_client.hset(token, 'answer', "answer")
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            mock_request.form.get = MagicMock(return_value='answer')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "answer")
            
            mock_request.form.get = MagicMock(return_value='aswer')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "aswer")
            
            mock_request.form.get = MagicMock(return_value='ansero')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "ansero")
            
            mock_request.form.get = MagicMock(return_value=' answer ')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", " answer ")
            
            mock_request.form.get = MagicMock(return_value='answpo')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "answer", "answpo")
            
            mock_request.form.get = MagicMock(return_value='nswera')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "nswera")
            
            mock_request.form.get = MagicMock(return_value='snwera')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "answer", "snwera")
            
            mock_request.form.get = MagicMock(return_value='extraanswer')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "extraanswer")
            
            mock_request.form.get = MagicMock(return_value='extraanswrt')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "extraanswrt")
            
            mock_request.form.get = MagicMock(return_value='extraanswft')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "answer", "extraanswft")
            
            mock_request.form.get = MagicMock(return_value='extranswera')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "answer", "extranswera")
            
            mock_request.form.get = MagicMock(return_value='extrasnwera')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "answer", "extrasnwera")
            
            
def test_check_answer_numbers_converted(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_fill_blank_facts"
    redis_client.hset(token, 'game_type', "fill_blank_facts")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            redis_client.hset(token, 'answer', "twenty two") # Numbers for real answers are converted to words before this process
            
            mock_request.form.get = MagicMock(return_value='22')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "twenty two", "twenty two")
            
            mock_request.form.get = MagicMock(return_value='twenty two')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "twenty two", "twenty two")
            
            mock_request.form.get = MagicMock(return_value='21')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "twenty two", "twenty one")
            
            mock_request.form.get = MagicMock(return_value='twenty one')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "twenty two", "twenty one")


def test_check_answer_fill_blank_facts(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_fill_blank_facts"
    redis_client.hset(token, 'game_type', "fill_blank_facts")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[0].param == "fill_blank_facts"
            
            redis_client.hset(token, 'answer', "Chris")
            
            mock_request.form.get = MagicMock(return_value='Chris')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "Chris", "Chris")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "Chris", "No answer given")
            
            mock_request.form.get = MagicMock(return_value='Christopher')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "Chris", "Christopher")
            
            mock_request.form.get = MagicMock(return_value='Chriss')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "Chris", "Chriss")
            
            mock_request.form.get = MagicMock(return_value='Chrid')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "Chris", "Chrid")
            
            mock_request.form.get = MagicMock(return_value='Chroddy')
            assert answer_checker.check_answer(token, games[0]) == (False, False, "Chris", "Chroddy")
            
            mock_request.form.get = MagicMock(return_value='Amazing Chris')
            assert answer_checker.check_answer(token, games[0]) == (True, False, "Chris", "Amazing Chris")
            
            
def test_check_answer_fill_blank_jokes_with_alternate_correct_answers(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_fill_blank_jokes"
    redis_client.hset(token, 'game_type', "fill_blank_jokes")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[1].param == "fill_blank_jokes"
            
            redis_client.hset(token, 'answer', "jugglers")
            
            mock_request.form.get = MagicMock(return_value='jugglers')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "jugglers", "jugglers")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[1]) == (False, False, "jugglers", "No answer given")
            
            mock_request.form.get = MagicMock(return_value='clowns')
            assert answer_checker.check_answer(token, games[1]) == (False, False, "jugglers", "clowns")
            
            redis_client.hset(token, 'answer', "laughter/laughing")
            
            mock_request.form.get = MagicMock(return_value='laughter')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "laughter/laughing", "laughter")
            
            mock_request.form.get = MagicMock(return_value='laughing')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "laughter/laughing", "laughing")
            
            mock_request.form.get = MagicMock(return_value='naughty')
            assert answer_checker.check_answer(token, games[1]) == (False, False, "laughter/laughing", "naughty")
            
            mock_request.form.get = MagicMock(return_value='laughign')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "laughter/laughing", "laughign")
            
            mock_request.form.get = MagicMock(return_value='laughinf')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "laughter/laughing", "laughinf")
            
            mock_request.form.get = MagicMock(return_value='laguhter')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "laughter/laughing", "laguhter")
            
            redis_client.hset(token, 'answer', "tiger/Siberian tiger")
            
            mock_request.form.get = MagicMock(return_value='tiger')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "tiger/Siberian tiger", "tiger")
            
            mock_request.form.get = MagicMock(return_value=' Siberian Tiger')
            assert answer_checker.check_answer(token, games[1]) == (True, False, "tiger/Siberian tiger", " Siberian Tiger")
            
            
            

def test_check_answer_trivia_madness_categories_with_two_thing_answer(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_madness_categories_topic"
    redis_client.hset(token, 'game_type', "trivia_madness_categories_topic")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[2].param == "trivia_madness_categories"
            
            redis_client.hset(token, 'answer', "flying fish")
            
            mock_request.form.get = MagicMock(return_value='flying fish')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "flying fish", "flying fish")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[2]) == (False, False, "flying fish", "No answer given")
            
            mock_request.form.get = MagicMock(return_value='flynig fish')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "flying fish", "flynig fish")
            
            mock_request.form.get = MagicMock(return_value='lying fish')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "flying fish", "lying fish")
            
            mock_request.form.get = MagicMock(return_value='lyin fish')
            assert answer_checker.check_answer(token, games[2]) == (False, False, "flying fish", "lyin fish")
            
            redis_client.hset(token, 'answer', "lion and tiger")
            
            mock_request.form.get = MagicMock(return_value='lion and tiger')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "lion and tiger", "lion and tiger")
            
            mock_request.form.get = MagicMock(return_value='tiger and lion')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "lion and tiger", "lion and tiger")
            
            mock_request.form.get = MagicMock(return_value='tiger & lion')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "lion and tiger", "lion & tiger")
            
            mock_request.form.get = MagicMock(return_value='tiget and lion')
            assert answer_checker.check_answer(token, games[2]) == (True, False, "lion and tiger", "lion and tiget")
            
            mock_request.form.get = MagicMock(return_value='tiget and liom')
            assert answer_checker.check_answer(token, games[2]) == (False, False, "lion and tiger", "liom and tiget")
            
            
def test_check_answer_trivia_madness(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_madness"
    redis_client.hset(token, 'game_type', "trivia_madness")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[3].param == "trivia_madness"
            
            redis_client.hset(token, 'answer', "The Sydney Opera House")
            
            mock_request.form.get = MagicMock(return_value='Sydney Opera House')
            assert answer_checker.check_answer(token, games[3]) == (True, False, "The Sydney Opera House", "Sydney Opera House")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[3]) == (False, False, "The Sydney Opera House", "No answer given")
            
            redis_client.hset(token, 'answer', "Green Horse")
            
            mock_request.form.get = MagicMock(return_value="It's the Green Horse")
            assert answer_checker.check_answer(token, games[3]) == (True, False, "Green Horse", "It's the Green Horse")
            
            mock_request.form.get = MagicMock(return_value="It's the Grey Horse")
            assert answer_checker.check_answer(token, games[3]) == (False, False, "Green Horse", "It's the Grey Horse")
            
            
def test_check_answer_trivia_mc_categories(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_mc_categories_topic"
    redis_client.hset(token, 'game_type', "trivia_mc_categories_topic")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[4].param == "trivia_mc_categories"
            
            redis_client.hset(token, 'answer', "The bright blue sky")
            
            mock_request.form.get = MagicMock(return_value='The bright blue sky')
            assert answer_checker.check_answer(token, games[4]) == (True, False, "The bright blue sky", "The bright blue sky")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[4]) == (False, False, "The bright blue sky", "No answer given")
            
            redis_client.hset(token, 'answer', 'He said, "I love you."')
            
            mock_request.form.get = MagicMock(return_value='He said, "I love you."')
            assert answer_checker.check_answer(token, games[4]) == (True, False, 'He said, "I love you."', 'He said, "I love you."')
            
            mock_request.form.get = MagicMock(return_value='He said, "I adore you."')
            assert answer_checker.check_answer(token, games[4]) == (False, False, 'He said, "I love you."', 'He said, "I adore you."')
            
            
def test_check_answer_trivia_mc(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_mc"
    redis_client.hset(token, 'game_type', "trivia_mc")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[5].param == "trivia_mc"
            
            redis_client.hset(token, 'answer', "Wilson")
            
            mock_request.form.get = MagicMock(return_value='Wilson')
            assert answer_checker.check_answer(token, games[5]) == (True, False, "Wilson", "Wilson")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[5]) == (False, False, "Wilson", "No answer given")
            
            mock_request.form.get = MagicMock(return_value='Anderson')
            assert answer_checker.check_answer(token, games[5]) == (False, False, "Wilson", "Anderson")
            
            
def test_check_answer_trivia_tf_categories(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_tf_categories_topic"
    redis_client.hset(token, 'game_type', "trivia_tf_categories_topic")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[6].param == "trivia_tf_categories"
            
            redis_client.hset(token, 'answer', "A rainbow has 7 colours.")
            redis_client.hset(token, 'question', "A rainbow has 7 colours.")
            
            mock_request.form.get = MagicMock(return_value='True')
            assert answer_checker.check_answer(token, games[6]) == (True, True, "A rainbow has 7 colours.", "True")
            
            mock_request.form.get = MagicMock(return_value='False')
            assert answer_checker.check_answer(token, games[6]) == (False, True, "A rainbow has 7 colours.", "False")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[6]) == (False, True, "A rainbow has 7 colours.", "")
            
            redis_client.hset(token, 'question', "A rainbow has 6 colours.")
            
            mock_request.form.get = MagicMock(return_value='False')
            assert answer_checker.check_answer(token, games[6]) == (True, False, "A rainbow has 7 colours.", "False")
            
            mock_request.form.get = MagicMock(return_value='True')
            assert answer_checker.check_answer(token, games[6]) == (False, False, "A rainbow has 7 colours.", "A rainbow has 6 colours.")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[6]) == (False, False, "A rainbow has 7 colours.", "")
            
            
def test_check_answer_trivia_tf(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_trivia_tf"
    redis_client.hset(token, 'game_type', "trivia_tf")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[7].param == "trivia_tf"
            
            redis_client.hset(token, 'answer', "The sun rises in the east.")
            redis_client.hset(token, 'question', "The sun rises in the east.")
            
            mock_request.form.get = MagicMock(return_value='True')
            assert answer_checker.check_answer(token, games[7]) == (True, True, "The sun rises in the east.", "True")
            
            mock_request.form.get = MagicMock(return_value='False')
            assert answer_checker.check_answer(token, games[7]) == (False, True, "The sun rises in the east.", "False")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[7]) == (False, True, "The sun rises in the east.", "")
            
            redis_client.hset(token, 'question', "The sun rises in the west.")
            
            mock_request.form.get = MagicMock(return_value='False')
            assert answer_checker.check_answer(token, games[7]) == (True, False, "The sun rises in the east.", "False")
            
            mock_request.form.get = MagicMock(return_value='True')
            assert answer_checker.check_answer(token, games[7]) == (False, False, "The sun rises in the east.", "The sun rises in the west.")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[7]) == (False, False, "The sun rises in the east.", "")
            
            
def test_check_answer_number_to_reach(test_app):
    
    random_token = secrets.token_hex(16)
    token = f"{random_token}_number_to_reach_mc"
    redis_client.hset(token, 'game_type', "number_to_reach_mc")
    redis_client.expire(token, 5)
    
    with test_app.test_request_context():
        with patch('Games0App.classes.answer_checker.request') as mock_request:
            
            assert games[8].param == "number_to_reach_mc"
            
            redis_client.hset(token, 'answer', "(10 + 14) + (12 - 2)")
            redis_client.hset(token, 'question', "Which of the following sums equates to 34?")
            
            mock_request.form.get = MagicMock(return_value='(10 + 14) + (12 - 2)')
            assert answer_checker.check_answer(token, games[8]) == (True, False, "(10 + 14) + (12 - 2) = 34", "(10 + 14) + (12 - 2)")
            
            mock_request.form.get = MagicMock(return_value='')
            assert answer_checker.check_answer(token, games[8]) == (False, False, "(10 + 14) + (12 - 2) = 34", "")
            
            mock_request.form.get = MagicMock(return_value='(14 + 14) + (12 - 2)')
            assert answer_checker.check_answer(token, games[8]) == (False, False, "(10 + 14) + (12 - 2) = 34", "(14 + 14) + (12 - 2)")

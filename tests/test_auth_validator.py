from unittest.mock import patch, MagicMock
from Games0App.__init__ import create_app
from Games0App.extensions import redis_client
from Games0App.models.log import Log
from Games0App.classes.auth_validator import auth_validator
import os

def test_validate_password_for_auth(test_app):
    
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request, \
                patch('Games0App.classes.auth_validator.current_user') as mock_current_user, \
                patch('Games0App.classes.auth_token_manager.current_user') as mock_current_user_2, \
                patch('Games0App.classes.auth_validator.send_email') as mock_send_email:
            
            redis_client.flushall()
            mock_request.form.get = MagicMock(return_value='password')
            mock_current_user.id = 1
            mock_current_user.password_hashed = b'$2b$12$/yCwu3uKdkdzKKN/ek.KCOJpdyrMhVxXyFI.39havwIpCFKWD4YI6'
            assert auth_validator.validate_password_for_auth() == True # First attempt
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_password_for_auth() == "Please enter your password." # Bypasses attempt check
            mock_current_user_2.id = 1
            mock_current_user_2.password_hashed = b'$2b$12$/yCwu3uKdkdzKKN/ek.KCOJpdyrMhVxXyFI.39havwIpCFKWD4YI6'
            mock_request.form.get = MagicMock(return_value='wrong_password')
            assert auth_validator.validate_password_for_auth() == "Something didn't match! Please try again." # Second attempt
            redis_client.flushall()
            for _ in range(2):
                assert auth_validator.validate_password_for_auth() == "Something didn't match! Please try again."
            for _ in range(11):
                assert auth_validator.validate_password_for_auth() == "This is not good! You'll have to wait 10 minutes."
            
            logs = Log.query.all()
            assert len(logs) == 1
            assert logs[0].id == 1
            assert logs[0].unique_id[0] == 'S'
            assert logs[0].user_id == 1
            assert logs[0].ip_address == None # This is a mock request
            assert logs[0].function_name == 'validate_password_for_auth'
            assert logs[0].log_type == 'max_auth_password_attempts'
            assert logs[0].timestamp != None
            assert not logs[0].data
            assert not logs[0].issue_id

def test_validate_new_user_name(test_app):
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:
            mock_request.form.get = MagicMock(return_value='test')
            assert auth_validator.validate_new_user_name() == True
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_user_name() == 'Please enter a username.'
            mock_request.form.get = MagicMock(return_value='a')
            assert auth_validator.validate_new_user_name() == 'Username must be at least 4 characters.'
            mock_request.form.get = MagicMock(return_value='a'*21)
            assert auth_validator.validate_new_user_name() == 'Username must be max 20 characters.'
            mock_request.form.get = MagicMock(return_value='test!')
            assert auth_validator.validate_new_user_name() == 'Username must only contain letters, numbers, underscores and hyphens.'

def test_validate_new_email(test_app):
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:
            mock_request.form.get = MagicMock(return_value='test@test.com')
            assert auth_validator.validate_new_email() == True
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_email() == 'Please enter an email.'
            mock_request.form.get = MagicMock(return_value='a')
            assert auth_validator.validate_new_email() == 'Email must be at least 3 characters.'
            mock_request.form.get = MagicMock(return_value='test.com')
            assert auth_validator.validate_new_email() == 'Please enter a valid email.'
            mock_request.form.get = MagicMock(return_value='test@@test.com')
            assert auth_validator.validate_new_email() == 'Please enter a valid email.'
            mock_request.form.get = MagicMock(return_value='test test@test.com')
            assert auth_validator.validate_new_email() == 'Please enter a valid email.'

def test_validate_new_password(test_app):
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        def custom_form_get_1(key):
            if key == 'password':
                return 'validPassword'
            elif key == 'confirm_password':
                return ''
            return None
        def custom_form_get_2(key):
            if key == 'password':
                return 'validPassword'
            elif key == 'confirm_password':
                return 'differentPassword'
            return None
        with patch('Games0App.classes.auth_validator.request') as mock_request:
            mock_request.form.get = MagicMock(return_value='validPassword')
            assert auth_validator.validate_new_password() == True
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_password() == ('Please enter a password.', 'password')
            mock_request.form.get = MagicMock(return_value='a'*7)
            assert auth_validator.validate_new_password() == ('Password must be at least 8 characters.', 'password')
            mock_request.form.get = MagicMock(side_effect=custom_form_get_1)
            assert auth_validator.validate_new_password() == ('Please confirm your password.', 'confirm_password')
            mock_request.form.get = MagicMock(side_effect=custom_form_get_2)
            assert auth_validator.validate_new_password() == ('Passwords do not match.', 'confirm_password')

def test_validate_victory_message(test_app):
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:
            mock_request.form.get = MagicMock(return_value='test')
            assert auth_validator.validate_victory_message() == True
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_victory_message() == True
            mock_request.form.get = MagicMock(return_value='a'*26)
            assert auth_validator.validate_victory_message() == "Max 25 characters."
            mock_request.form.get = MagicMock(return_value='Shit!') # I sincerely apologise for this
            assert auth_validator.validate_victory_message() == "Contains bad language."

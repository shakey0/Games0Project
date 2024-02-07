from unittest.mock import patch, MagicMock
from Games0App.__init__ import create_app
from Games0App.extensions import redis_client
from Games0App.models.log import Log
from Games0App.models.email_log import EmailLog
from Games0App.classes.auth_validator import auth_validator
import os


def test_validate_password_for_auth(test_app):
    
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request, \
            patch('Games0App.classes.auth_validator.current_user') as mock_current_user, \
            patch('Games0App.classes.auth_token_manager.current_user') as mock_current_user_2:
            
            redis_client.flushall() # Clear Redis cache
            mock_current_user.id = 1
            mock_current_user_2.id = 1
            mock_current_user.username = 'username'
            mock_current_user.email = 'user@example.com'
            mock_current_user.password_hashed = b'$2b$12$/yCwu3uKdkdzKKN/ek.KCOJpdyrMhVxXyFI.39havwIpCFKWD4YI6'

            # Test the function with a correct password
            mock_request.form.get = MagicMock(return_value='password')
            assert auth_validator.validate_password_for_auth() == True # First attempt

            # Test the function with a blank password
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_password_for_auth() == "Please enter your password." # Bypasses attempt check
            
            # Test the function with a wrong password
            mock_request.form.get = MagicMock(return_value='wrong_password')
            assert auth_validator.validate_password_for_auth() == "Something didn't match! Please try again." # Second attempt
            
            redis_client.flushall() # Clear Redis cache

            # Test the function with a wrong password 2 twice and then the correct password
            for _ in range(2):
                assert auth_validator.validate_password_for_auth() == "Something didn't match! Please try again."
            mock_request.form.get = MagicMock(return_value='password')
            assert auth_validator.validate_password_for_auth() == True # Third attempt

            redis_client.flushall() # Clear Redis cache

            # Test the function with a wrong password 13 times
            mock_request.form.get = MagicMock(return_value='wrong_password')
            for _ in range(2):
                assert auth_validator.validate_password_for_auth() == "Something didn't match! Please try again."
            for _ in range(11):
                assert auth_validator.validate_password_for_auth() == "This is not good! You'll have to wait 10 minutes."
            
            # Check the log has been created in the database
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

            # Check the email log has been created in the database
            email_logs = EmailLog.query.all()
            assert len(email_logs) == 1
            assert email_logs[0].id == 1
            assert email_logs[0].user_email == 'user@example.com'
            assert email_logs[0].username == 'username'
            assert email_logs[0].email_type == 'auth_password_max_attempts'
            assert email_logs[0].info == {}
            assert email_logs[0].unique_id[0] == 'S'
            assert email_logs[0].status_code == 200
            assert email_logs[0].json_response == {'success': True}
            assert email_logs[0].timestamp != None


def test_validate_new_user_name(test_app):

    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:

            # Test the function with a valid username
            mock_request.form.get = MagicMock(return_value='test')
            assert auth_validator.validate_new_user_name() == True

            # Test the function with an empty username
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_user_name() == 'Please enter a username.'

            # Test the function with a username that is too short
            mock_request.form.get = MagicMock(return_value='a')
            assert auth_validator.validate_new_user_name() == 'Username must be at least 4 characters.'

            # Test the function with a username that is too long
            mock_request.form.get = MagicMock(return_value='a'*21)
            assert auth_validator.validate_new_user_name() == 'Username must be max 20 characters.'

            # Test the function with a username that contains invalid characters
            mock_request.form.get = MagicMock(return_value='test!')
            assert auth_validator.validate_new_user_name() == 'Username must only contain letters, numbers, underscores and hyphens.'


def test_validate_new_email(test_app):

    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:

            # Test the function with a valid email
            mock_request.form.get = MagicMock(return_value='test@test.com')
            assert auth_validator.validate_new_email() == True

            # Test the function with an empty email
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_email() == 'Please enter an email.'

            # Test the function with an email that is too short
            mock_request.form.get = MagicMock(return_value='a')
            assert auth_validator.validate_new_email() == 'Email must be at least 3 characters.'

            # Test the function with an email that does not contain an @ symbol
            mock_request.form.get = MagicMock(return_value='test.com')
            assert auth_validator.validate_new_email() == 'Please enter a valid email.'

            # Test the function with an email that contains 2 @ symbols
            mock_request.form.get = MagicMock(return_value='test@@test.com')
            assert auth_validator.validate_new_email() == 'Please enter a valid email.'

            # Test the function with an email that contains a space
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

            # Test the function with a valid password
            mock_request.form.get = MagicMock(return_value='validPassword')
            assert auth_validator.validate_new_password() == True

            # Test the function with an empty password
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_new_password() == ('Please enter a password.', 'password')

            # Test the function with a password that is too short
            mock_request.form.get = MagicMock(return_value='a'*7)
            assert auth_validator.validate_new_password() == ('Password must be at least 8 characters.', 'password')

            # Test the function with an empty confirm password
            mock_request.form.get = MagicMock(side_effect=custom_form_get_1)
            assert auth_validator.validate_new_password() == ('Please confirm your password.', 'confirm_password')

            # Test the function with a password that does not match the confirm password
            mock_request.form.get = MagicMock(side_effect=custom_form_get_2)
            assert auth_validator.validate_new_password() == ('Passwords do not match.', 'confirm_password')


def test_validate_victory_message(test_app):

    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context(), app.test_request_context():
        with patch('Games0App.classes.auth_validator.request') as mock_request:

            # Test the function with a valid victory message
            mock_request.form.get = MagicMock(return_value='test')
            assert auth_validator.validate_victory_message() == True

            # Test the function with an empty victory message (this is allowed)
            mock_request.form.get = MagicMock(return_value='')
            assert auth_validator.validate_victory_message() == True

            # Test the function with a victory message that is too long
            mock_request.form.get = MagicMock(return_value='a'*26)
            assert auth_validator.validate_victory_message() == "Max 25 characters."

            # Test the function with a victory message that contains bad language
            mock_request.form.get = MagicMock(return_value='Shit!') # I sincerely apologise for this
            assert auth_validator.validate_victory_message() == "Contains bad language."

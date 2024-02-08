from unittest.mock import patch
from Games0App.extensions import redis_client
from Games0App.models.log import Log
from Games0App.classes.auth_token_manager import auth_token_manager


@patch('Games0App.classes.auth_token_manager.current_user')
def test_check_reset_password_attempt(mock_current_user):

    redis_client.flushall()
    mock_current_user.id = 1

    # Test check_reset_password_attempt (only 1 attempt allowed)
    assert auth_token_manager.check_reset_password_attempt() == True
    auth_token_manager.attempt_check('reset_password', 1)
    assert auth_token_manager.check_reset_password_attempt() == False


@patch('Games0App.classes.auth_token_manager.current_user')
def test_check_auth_password_attempt(mock_current_user):

    redis_client.flushall()
    mock_current_user.id = 1

    # Due to the design flow of the code, when this function is called, there should always be a previous attempt
    assert auth_token_manager.check_auth_password_attempt() == False

    # Test check_auth_password_attempt (3 attempts allowed)
    for _ in range(2):
        auth_token_manager.attempt_check('auth_password', 1)
        assert auth_token_manager.check_auth_password_attempt() == True
    auth_token_manager.attempt_check('auth_password', 1)
    assert auth_token_manager.check_auth_password_attempt() == False


def test_check_login_password_attempt():

    redis_client.flushall()

    # Due to the design flow of the code, when this function is called, there should always be a previous attempt
    assert auth_token_manager.check_login_password_attempt('test') == False

    # Test check_login_password_attempt (5 attempts allowed)
    for _ in range(4):
        auth_token_manager.attempt_check('login_password', 'test')
        assert auth_token_manager.check_login_password_attempt('test') == True
    auth_token_manager.attempt_check('login_password', 'test')
    assert auth_token_manager.check_login_password_attempt('test') == False


@patch('Games0App.classes.auth_token_manager.current_user')
def test_attempt_check(mock_current_user):

    redis_client.flushall()
    mock_current_user.id = 1

    # Test attempt_check for reset_password (only 1 attempt allowed)
    assert auth_token_manager.attempt_check('reset_password', 1) == True
    assert auth_token_manager.attempt_check('reset_password', 1) == False

    # Test attempt_check for reset_password_email_first (only 1 attempt allowed)
    assert auth_token_manager.attempt_check('reset_password_email_first', 1) == True
    assert auth_token_manager.attempt_check('reset_password_email_first', 1) == False

    # Test attempt_check for reset_password_email (3 attempts allowed)
    for _ in range(3):
        assert auth_token_manager.attempt_check('reset_password_email', 1) == True
    for _ in range(11):
        assert auth_token_manager.attempt_check('reset_password_email', 1) == False
        # reset_password_email deletes the key for reset_password_email_first to avoid overlogging
        assert auth_token_manager.attempt_check('reset_password_email_first', 1) == True
        assert auth_token_manager.attempt_check('reset_password_email_first', 1) == False

    # Test attempt_check for auth_password (3 attempts allowed)
    for _ in range(3):
        assert auth_token_manager.attempt_check('auth_password', 1) == True
    assert auth_token_manager.attempt_check('auth_password', 1) == False

    # Test attempt_check for login_password (5 attempts allowed)
    for _ in range(5):
        assert auth_token_manager.attempt_check('login_password', 1) == True
    assert auth_token_manager.attempt_check('login_password', 1) == False

    # Test attempt_check for route (10 attempts allowed)
    for _ in range(10):
        assert auth_token_manager.attempt_check('route', 1) == True
    assert auth_token_manager.attempt_check('route', 1) == False


def test_get_verify_delete_reset_password_link_token():
    
    redis_client.flushall()

    # Test all functions for reset_password_link_token
    token = auth_token_manager.get_reset_password_link_token(1)
    assert len(token) == 32
    assert auth_token_manager.verify_reset_password_link_token(token) == 1
    auth_token_manager.delete_reset_password_link_token(token)
    assert auth_token_manager.verify_reset_password_link_token(token) == None


def test_get_new_add_values_to_get_values_from_delete_auth_token(test_app):
    
    redis_client.flushall()

    # Get new auth token
    token = auth_token_manager.get_new_auth_token(
        {'user_id': 1, 'username': 'test', 'route': 'change_password', 'stage': 1}
    )
    
    # Check if the log was created in the database
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 1
    assert logs[0].ip_address == 'unknown'
    assert logs[0].function_name == 'get_new_auth_token'
    assert logs[0].log_type == 'init_change_password'
    assert logs[0].timestamp != None
    assert logs[0].data['username'] == 'test'
    assert logs[0].data['route'] == 'change_password'
    assert not logs[0].issue_id
    
    # Test get_values_from_auth_token and add_values_to_auth_token
    assert len(token) == 32
    assert auth_token_manager.get_values_from_auth_token(token, ['user_id', 'username', 'route', 'stage']) == {'user_id': '1', 'username': 'test', 'route': 'change_password', 'stage': '1'}
    
    # Test add_values_to_auth_token
    auth_token_manager.add_values_to_auth_token(token, {'user_id': '1', 'username': 'test', 'route': 'change_password', 'stage': 2, 'new': 'new'})
    assert auth_token_manager.get_values_from_auth_token(token, ['user_id', 'username', 'route', 'stage', 'new']) == {'user_id': '1', 'username': 'test', 'route': 'change_password', 'stage': '2', 'new': 'new'}
    
    # Test getting an estranged value yields None
    assert auth_token_manager.get_values_from_auth_token(token, ['user_id', 'username', 'route', 'stage', 'new', 'another']) == {'user_id': '1', 'username': 'test', 'route': 'change_password', 'stage': '2', 'new': 'new', 'another': None}
    
    # Test delete_auth_token
    auth_token_manager.delete_auth_token(token)
    assert auth_token_manager.get_values_from_auth_token(token, ['user_id', 'username', 'route', 'stage', 'new', 'another']) == {'user_id': None, 'username': None, 'route': None, 'stage': None, 'new': None, 'another': None}

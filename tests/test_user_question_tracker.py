from unittest.mock import patch, MagicMock
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from Games0App.classes.user_question_tracker import user_question_tracker
import os

def test_store_last_50_questions(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    with patch('Games0App.classes.user_question_tracker.current_user') as mock_current_user:
        mock_current_user.id = 1
        game_string = 'game2'
        question_bundle_ids = ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id']
        user_question_tracker.store_last_50_questions(game_string, question_bundle_ids)
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}

def test_cache_questions(test_app):

    game2questions = []
    for _ in range(60):
        game2questions.append(os.urandom(16).hex())

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': game2questions, 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    with patch('Games0App.classes.user_question_tracker.current_user') as mock_current_user:
        
        redis_client.flushall()
        mock_current_user.id = 1
        game_string = 'game2'
        user_question_tracker.cache_questions(game_string)
        cached_questions_ids = redis_client.lrange('1_question_cache_game2', 0, -1)
        assert len(cached_questions_ids) == 50
        for id in cached_questions_ids:
            assert id.decode('utf-8') in game2questions
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': game2questions[10:], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}

def test_deposit_question(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    redis_client.flushall()
    redis_client.rpush('1_question_cache_game2', *['gksl3jl33', 'kafbasf98', '1k1a8fffs'])

    with patch('Games0App.classes.user_question_tracker.current_user') as mock_current_user:

        mock_current_user.id = 1
        game_string = 'game2'
        question_id = 'new_question_id'
        assert user_question_tracker.deposit_question(game_string, question_id) == True
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
        cached_questions_ids = redis_client.lrange('1_question_cache_game2', 0, -1)
        assert len(cached_questions_ids) == 4
        for id in cached_questions_ids:
            assert id.decode('utf-8') in ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id']

        question_id = 'kafbasf98'
        assert user_question_tracker.deposit_question(game_string, question_id) == False
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
        cached_questions_ids = redis_client.lrange('1_question_cache_game2', 0, -1)
        assert len(cached_questions_ids) == 4
        for id in cached_questions_ids:
            assert id.decode('utf-8') in ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id']

def test_deposit_question_unauth(test_app):
    
        redis_client.flushall()
        redis_client.rpush('111_unauth_question_cache_game2', *['gksl3jl33', 'kafbasf98', '1k1a8fffs'])
    
        with patch('Games0App.classes.user_question_tracker.current_user') as mock_current_user:
    
            game_string = 'game2'
            question_id = 'new_question_id'
            token = '111'
            assert user_question_tracker.deposit_question_unauth(game_string, question_id, token) == True
            cached_questions_ids = redis_client.lrange('111_unauth_question_cache_game2', 0, -1)
            assert len(cached_questions_ids) == 4
            for id in cached_questions_ids:
                assert id.decode('utf-8') in ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id']
    
            question_id = 'kafbasf98'
            assert user_question_tracker.deposit_question_unauth(game_string, question_id, token) == False
            cached_questions_ids = redis_client.lrange('111_unauth_question_cache_game2', 0, -1)
            assert len(cached_questions_ids) == 4
            for id in cached_questions_ids:
                assert id.decode('utf-8') in ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_id']

def test_deposit_question_bundle(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    with patch('Games0App.classes.user_question_tracker.current_user') as mock_current_user:

        mock_current_user.id = 1
        game_string = 'game2'
        question_bundle_ids = ['new_question_1', 'new_question_2', 'new_question_3']
        user_question_tracker.deposit_question_bundle(question_bundle_ids, game_string)
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs', 'new_question_1', 'new_question_2', 'new_question_3'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}

        question_bundle_ids = ['new_question_3', 'new_question_5', 'new_question_6', '1k1a8fffs']
        user_question_tracker.deposit_question_bundle(question_bundle_ids, game_string)
        user = db.session.query(User).filter(User.id == 1).first()
        assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', 'new_question_1', 'new_question_2', 'new_question_3', 'new_question_5', 'new_question_6', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}

from Games0App import db
from Games0App.models.user import User
from Games0App.models.high_score import HighScore
from datetime import datetime
import pytest
from sqlalchemy.exc import IntegrityError

def test_high_score_creation(test_app):
        
    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()
    
    test_score = HighScore(
        user_id=1,
        game='game1',
        game_name='game1',
        category='category1',
        difficulty='easy',
        score=100,
        date='2021-01-01 00:00:00',
        message='test message',
        likes=0
    )
    db.session.add(test_score)
    db.session.commit()

    score = HighScore.query.filter_by(game='game1').first()
    assert score is not None
    assert score.id == 1
    assert score.user_id == 1
    assert score.game == 'game1'
    assert score.game_name == 'game1'
    assert score.category == 'category1'
    assert score.difficulty == 'easy'
    assert score.score == 100
    assert score.date == datetime(2021, 1, 1, 0, 0, 0)
    assert score.message == 'test message'
    assert score.likes == 0

def test_high_score_creation_fail_non_present_user_id(test_app):

    test_score = HighScore(
        user_id=1,
        game='game1',
        game_name='game1',
        category='category1',
        difficulty='easy',
        score=100,
        date='2021-01-01 00:00:00',
        message='test message',
        likes=0
    )
    db.session.add(test_score)
    with pytest.raises(IntegrityError):
        db.session.commit()

def test_high_score_instances_are_equal(test_app):
        
        score1 = HighScore(
            id=1,
            user_id=1,
            game='game1',
            game_name='game1',
            category='category1',
            difficulty='easy',
            score=100,
            date='2021-01-01 00:00:00',
            message='test message',
            likes=0
        )
        score2 = HighScore(
            id=1,
            user_id=1,
            game='game1',
            game_name='game1',
            category='category1',
            difficulty='easy',
            score=100,
            date='2021-01-01 00:00:00',
            message='test message',
            likes=0
        )
        assert score1 == score2

def test_high_score_instances_are_not_equal(test_app):
        
        score1 = HighScore(
            id=1,
            user_id=1,
            game='game1',
            game_name='game1',
            category='category1',
            difficulty='easy',
            score=100,
            date='2021-01-01 00:00:00',
            message='test message',
            likes=0
        )
        score2 = HighScore(
            id=2,
            user_id=1,
            game='game1',
            game_name='game1',
            category='category1',
            difficulty='easy',
            score=100,
            date='2021-01-01 00:00:00',
            message='test message',
            likes=0
        )
        assert score1 != score2

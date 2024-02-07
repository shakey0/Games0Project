from Games0App import db
from Games0App.models.user import User
import pytest
from sqlalchemy.exc import IntegrityError


def test_user_creation(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    user = User.query.filter_by(username='john_doe').first()
    assert user is not None
    assert user.id == 1
    assert user.username == 'john_doe'
    assert user.email == 'john@example.com'
    assert user.password_hashed == b'fake_password_hashed'
    assert user.last_50_questions == {'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'], 'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}


def test_user_creation_fail_non_unique_username(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    test_user = User(
        username='john_doe',
        email='john2@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_user_creation_fail_non_unique_email(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    test_user = User(
        username='john_doe2',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_user_creation_fail_non_unique_username_email(test_app):

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    db.session.commit()

    test_user = User(
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    db.session.add(test_user)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_user_instances_are_equal(test_app):

    user1 = User(
        id=1,
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    user2 = User(
        id=1,
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    assert user1 == user2


def test_user_instances_are_not_equal(test_app):

    user1 = User(
        id=1,
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    user2 = User(
        id=2,
        username='john_doe',
        email='john@example.com',
        password_hashed=b'fake_password_hashed',
        last_50_questions={
            'game1': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game2': ['gksl3jl33', 'kafbasf98', '1k1a8fffs'],
            'game3': ['gksl3jl33', 'kafbasf98', '1k1a8fffs']}
    )
    assert user1 != user2

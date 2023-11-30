from Games0App.models.user import User

def test_user_creation(test_app, test_client, seed_test_database):
    user = User.query.filter_by(username='john_doe').first()
    assert user is not None
    assert user.username == 'john_doe'
    assert user.email == 'john@example.com'

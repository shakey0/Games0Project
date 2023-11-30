from Games0App.models.user import User

def init_user(db):

    test_user = User(
        username='john_doe',
        email='john@example.com'
    )
    db.session.add(test_user)
    db.session.commit()

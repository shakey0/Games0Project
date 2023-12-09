from Games0App import db
from sqlalchemy.dialects.postgresql import JSONB

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)  # VALIDATE LENGTH WITH JAVASCRIPT
    email = db.Column(db.String(120), index=True, unique=True)  # VALIDATE EMAIL WITH JAVASCRIPT
    password_hashed = db.Column(db.String(128))  # VALIDATE STRENGTH WITH JAVASCRIPT
    games_played = db.Column(JSONB)
    games_tracker = db.Column(JSONB)

    def __repr__(self):
        return '<User {}>'.format(self.username)

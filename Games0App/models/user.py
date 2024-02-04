from Games0App import db
from sqlalchemy.dialects.postgresql import JSONB, BYTEA, CITEXT
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(CITEXT, index=True, unique=True)
    password_hashed = db.Column(BYTEA)
    last_50_questions = db.Column(JSONB)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User {}>'.format(self.username)

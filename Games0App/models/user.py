from Games0App import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import BYTEA
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hashed = db.Column(BYTEA)

    def __repr__(self):
        return '<User {}>'.format(self.username)

from Games0App import db

class HighScore(db.Model):
    __tablename__ = 'high_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    game = db.Column(db.String(50))
    game_name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(10))
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    message = db.Column(db.String(200))
    likes = db.Column(db.Integer)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<HighScores {}>'.format(self.game)

# Keeps track of which users have liked which scores
scores_users = db.Table('scores_users',
    db.Column('score_id', db.Integer, db.ForeignKey('high_scores.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

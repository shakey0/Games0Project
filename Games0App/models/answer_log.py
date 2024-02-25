from Games0App import db

class AnswerLog(db.Model):
    __tablename__ = 'answer_logs'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(100))
    difficulty = db.Column(db.String(10))
    question_id = db.Column(db.String(50))
    real_answer = db.Column(db.String(100))
    user_answer = db.Column(db.String(100))
    correct = db.Column(db.Boolean)
    seconds_to_answer = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<AnswerLog {}>'.format(self.id)

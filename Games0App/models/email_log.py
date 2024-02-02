from Games0App import db
from sqlalchemy.dialects.postgresql import JSONB

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), index=True)
    username = db.Column(db.String(20))
    email_type = db.Column(db.String(50))
    info = db.Column(JSONB)
    unique_id = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    json_response = db.Column(JSONB)
    timestamp = db.Column(db.DateTime)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<EmailLog {}>'.format(self.id)

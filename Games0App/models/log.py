from Games0App import db
from sqlalchemy.dialects.postgresql import JSONB

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), index=True)
    user_id = db.Column(db.Integer, index=True)
    ip_address = db.Column(db.String(20))
    function_name = db.Column(db.String(50))
    log_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    data = db.Column(JSONB)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<Log {}>'.format(self.id)

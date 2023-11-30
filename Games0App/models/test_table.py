from Games0App import db

class RunTable(db.Model):
    __tablename__ = 'test_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

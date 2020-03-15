from datetime import datetime
from flaskblog import db


class QueryT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    origterm = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.term}', '{self.date_posted}')"


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    terminology = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return f"Dictionary('{self.terminology}', '{self.id}')"

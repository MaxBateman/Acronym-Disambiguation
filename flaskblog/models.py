from datetime import datetime
from flaskblog import db
#from flask import current_app


class QueryT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    origterm = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    percentmatch = db.Column(db.String(3), nullable=False)
    origtermpresent = db.Column(db.Boolean, nullable=False)
    acrmatches = db.Column(db.Text)
    lfmatches = db.Column(db.Text)

    def __repr__(self):
        return f"Post('{self.term}', '{self.date_posted}')"


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    terminology = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return f"Dictionary('{self.terminology}', '{self.id}')"

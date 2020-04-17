from datetime import datetime
from flaskblog import db
#from flask import current_app


class QueryT(db.Model):
    __tablename__ = 'queryt'
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    origterm = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    percentmatch = db.Column(db.String(3), nullable=False)
    origtermpresent = db.Column(db.Boolean, nullable=False)
    acrmatches = db.Column(db.Text)
    lfmatches = db.Column(db.Text)
    user_id = db.Column(db.String(50), nullable=False)


    def __repr__(self):
        return f"Post('{self.term}', '{self.date_posted}')"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    abstract = db.Column(db.Text)
    doi = db.Column(db.String(20))
    publication_date = db.Column(db.DateTime)
    query_id = db.Column(db.Integer, db.ForeignKey('queryt.id'), nullable=False)
    queries = db.relationship('QueryT', backref='author', lazy=True)



class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    terminology = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return f"Dictionary('{self.terminology}', '{self.id}')"

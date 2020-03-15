from datetime import datetime
from flaskblog import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.term}', '{self.date_posted}')"

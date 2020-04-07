from flask import render_template, Blueprint, redirect, url_for, session
from flaskblog import db, sess
from flaskblog.models import QueryT
from sqlalchemy import event
import time
main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    db.create_all()
    queriest = QueryT.query.filter_by(user_id=session.sid)
    queriest = queriest[::-1]

    return render_template('home.html', queriest=queriest, active1="", active2="active")


@main.route("/about")
def about():
    #run_shelly()
    return render_template('about.html', title='About')


@main.route("/home/all")
def home_all():
    queriest = QueryT.query.all()
    queriest = queriest[::-1]
    return render_template('home.html', queriest=queriest, active1="", active2="active")
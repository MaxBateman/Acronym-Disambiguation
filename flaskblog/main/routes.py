from flask import render_template, Blueprint, redirect, url_for, session, request, flash, Markup
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
    try:
        queriest[0]
    except IndexError:
        flash(Markup('Create a <a href="{{ url_for('main.create_queryt') }}">new query!</a>', 'success'))
    page = request.args.get('page', 1, type=int)
    queriest = queriest.order_by(QueryT.date_posted.desc()).paginate(page=page, per_page=5)

    return render_template('home.html', queriest=queriest, active1="active", active2="")


@main.route("/about")
def about():
    #run_shelly()
    return render_template('about.html', title='About', legend='About')


@main.route("/home/all")
def home_all():
    page = request.args.get('page', 1, type=int)
    queriest = QueryT.query.order_by(QueryT.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', queriest=queriest, active1="", active2="active")
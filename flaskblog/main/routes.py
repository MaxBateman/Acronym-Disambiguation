from flask import render_template, Blueprint, redirect, url_for
from flaskblog import db
from flaskblog.models import QueryT
from sqlalchemy import event
import time
main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
#@event.listens_for(db.session, "after_commit")
def home():
    db.create_all()
    queriest = QueryT.query.all()
    queriest = queriest[::-1]
    #tick_file = os.path.join(os.getcwd(), 'flaskblog/static/tick.png')
    #if num matched > 0
    #picture_file = "tickg.jpg"
    return render_template('home.html', queriest=queriest)


#@event.listens_for(db.session, 'after_commit')
#def receive_after_commit(session):
#    print(696969669)
#    return redirect(url_for('main.about'))


@main.route("/about")
def about():
    #run_shelly()
    return render_template('about.html', title='About')

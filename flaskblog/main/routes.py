from flask import render_template, Blueprint
from flaskblog import db
from flaskblog.models import QueryT

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    db.create_all()
    queriest = QueryT.query.all()
    queriest = queriest[::-1]
    #tick_file = os.path.join(os.getcwd(), 'flaskblog/static/tick.png')
    #if num matched > 0
    #picture_file = "tickg.jpg"
    return render_template('home.html', queriest=queriest)


@main.route("/about")
def about():
    #run_shelly()
    return render_template('about.html', title='About')

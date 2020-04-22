from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config
import redis
from flask_mail import Mail
from flask_rq2 import RQ
db = SQLAlchemy()
sess = Session()
rq = RQ()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    sess.init_app(app)
    mail.init_app(app)
    from flaskblog.queries.routes import queries
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(queries)
    rq.init_app(app)#mo
    app.register_blueprint(main)
    app.register_blueprint(errors)


    return app

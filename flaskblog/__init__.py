from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config
import redis
from flask_rq2 import RQ
db = SQLAlchemy()

rq = RQ()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from flaskblog.queries.routes import queries
    from flaskblog.main.routes import main
    app.register_blueprint(queries)
    rq.init_app(app)
    app.register_blueprint(main)


    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config
import redis
from rq import Queue
db = SQLAlchemy()

r = redis.Redis()
q = Queue(connection = r)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from flaskblog.queries.routes import queries
    from flaskblog.main.routes import main
    app.register_blueprint(queries)
    app.register_blueprint(main)


    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, DDL
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from sqlalchemy_utils import functions


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'f33eb5d45b89dd2e5c07a75c96835848'
db = SQLAlchemy(app)



from flaskblog import routes

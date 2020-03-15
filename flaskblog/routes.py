from flask import render_template, url_for, flash, redirect
from flaskblog import app, db
from flaskblog.forms import PostForm
from flaskblog.models import Post
from pymed import PubMed
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import requests
import json

from sqlalchemy_utils import functions
if not functions.database_exists('sqlite:///site.db'):
    db.create_all()

stop_words = stopwords.words('english')
pubmed = PubMed(tool = "PubMedSearch", email = "maxmoneywells@gmail.com")


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    posts = posts[::-1]
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


abstract = ""


@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        terms = get_terms(get_pubmed(form.term.data))

        # stringl = ""
        # for key in terms["terms"]:
        #     stringl = stringl , terms["terms"][key]
        stringl = ""
        for key in terms["terms"]:
            stringl = stringl + " 1 " + key

        post = Post(term=form.term.data, content=stringl)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


def get_terms(fulltext):
    url = "https://translated-terminology-extraction-v1.p.rapidapi.com/get.php"
    querystring = {"lang":"en","text":fulltext}
    headers = {
        'x-rapidapi-host': "translated-terminology-extraction-v1.p.rapidapi.com",
        'x-rapidapi-key': "7b04c4070bmshaf8f4632d54293fp13aac9jsnb40fba917447"
        }
    response = requests.get( url, headers=headers, params=querystring)

    return response.json()


def get_pubmed(term):
    results = pubmed.query(term, max_results=1)
    counter = 0
    for article in results:
        abstract = article.abstract
        if abstract is None:
            abstract = "None"
        counter = counter + 1
    return abstract


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.term, post=post)


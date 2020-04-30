from flask import Blueprint, render_template, url_for, redirect, flash, Markup, session, current_app
from flaskblog import db, sess, mail
from flaskblog.queries.forms import QuerytForm, Email
from flaskblog.models import QueryT, Dictionary, Article
from flaskblog.queries.utils import *
import time
from flaskblog.config import ADMINS
import os

from sqlalchemy import event
from flaskblog import rq
from rq.job import Job
from flask_mail import Message
queries = Blueprint('queries',__name__)


@queries.route("/queriest/new", methods=['GET', 'POST'])
def new_queryt():
    existy = Dictionary.query.filter_by(id=1).first()
    if existy is None:
        def insert_initial_dict():
            #print(os.getcwd())
            dict_file = os.path.join(os.getcwd(), 'flaskblog/static/termin.txt')
            fh = open(dict_file)
            for line in fh:
                #print(1, existy)
                termo = Dictionary(terminology=line)
                db.session.add(termo)
            db.session.commit()

        insert_initial_dict()
    form = QuerytForm()

    if form.validate_on_submit():
        #terms = get_terms(get_pubmed(form.term.data))
        flashed = False
        tempterm = form.term.data
        if form.term.data[0] == " ":
            tempterm = form.term.data.strip()
        user_id = session.sid
        potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(tempterm[0])).all()
        qt = get_inp.queue(form.term.data, potential_full, user_id)
        counter =0
        while qt.result != form.term.data:
            time.sleep(1)
            print(qt.result)
            if qt.result == True:
                flashed = True
                flash('Your query has not been created!', 'danger')
                break
                
            counter = counter +1
            if counter == 5:
                flashed = True
                flash('Your query may still be pending, please refresh the page in a few seconds.', 'warning')
                break
        #qt = Job.fetch('form.term.data', rq)
        #print(qt.get_status())
        #c = False
        #while not qt.get_status() == "finished":
        #    time.sleep(0.2)
        #    print(qt.get_status())
        print(qt.result)

        if not flashed:
            flash('Your query has been created!', 'success')
            return redirect(url_for('queries.queryt', queryt_id=qt.result.id))
        return redirect(url_for('main.home'))
         #   check_match(abstracts, term)
    return render_template('create_queryt.html', title='New Query',
                           form=form, legend='New Query')


@queries.route("/egg/<sterm>/<termdata>", methods=['GET'])
def egg(sterm, termdata):
    user_id = session.sid
    potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(sterm[0])).all()
    qt = get_inp.queue(sterm, potential_full, user_id, termdata)
    counter =0
    flashed = False
    while qt.result.origterm != sterm:
        time.sleep(1)
        print(qt.result, termdata)
        if qt.result == True:
                flashed = True
                flash('Your query has not been created!', 'danger')
                break
                
        counter = counter +1
        if counter == 5:
            flashed = True
            flash('Your query may still be pending, please refresh the page in a few seconds.', 'warning')
            break

    if not flashed:
            flash('Your query has been created!', 'success')
    return redirect(url_for('main.home'))


@queries.route("/queryt/<int:queryt_id>", methods=['GET', 'POST'])
def queryt(queryt_id):
    queryt = QueryT.query.get_or_404(queryt_id)
    articles = Article.query.filter_by(query_id=queryt_id)
    lfmatches = None
    acrmatches = None
    
    if queryt.lfmatches:
        lfmatches = queryt.lfmatches.split(", ")
    acrreplace = []
    if queryt.acrmatches:
        acrmatches = queryt.acrmatches.split(", ")
        for article in articles:
            for term in acrmatches:
                termb = "("+term+")"
                if term.lower() == queryt.origterm.lower():
                    article.abstract = article.abstract.replace(termb, '<mark class="acrmatch">'+termb+'</mark>')
                else:
                    article.abstract = article.abstract.replace(termb, '<mark class="acr">'+termb+'</mark>')
            article.abstract = Markup(article.abstract)

    form = Email()
    if form.is_submitted():
        if form.validate_on_submit():
            send_email.queue("ACRPUBMED - ", ADMINS[0], [form.email.data],'hell')
            
            #send_em(msg)
            flash('Email Sent!', 'success')

            return redirect(url_for('queries.queryt', queryt_id=queryt.id))
        else:
            
            flash('Invalid Email!', 'danger')
            return redirect(url_for('queries.queryt', queryt_id=queryt.id))
    return render_template('queryt.html', form=form, title=queryt.term, queryt=queryt, lfmatches=lfmatches, acrmatches=acrmatches, content=articles)


@rq.job
def get_inp(data, potential_full, user_id, termdata=None):
    time.sleep(0.35)
    search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches, results, failed = inp(data, potential_full, termdata)
    print("done")
    queryt = QueryT(origterm=search_term, term=fword, content=abstracts, percentmatch=percentmatch,
                    origtermpresent=present, acrmatches=acrmatches, lfmatches=lfmatches, user_id=user_id)
    if not failed:    
        for article in results:
            abstract = article.abstract
            title = article.title
            doi = article.doi
            publication_date = article.publication_date

            queryt.author.append(Article(title=title, abstract=abstract, doi=doi, publication_date=publication_date))
        db.session.add(queryt)
        db.session.flush()
        qid = queryt.id
        db.session.commit()
        return queryt
    return failed


@rq.job
def send_email(subject,sender,recipients,text_body):
    print(subject,sender,recipients,text_body)
    msg = Message(subject, sender=sender, recipients=recipients)
    print(1)
    msg.body=text_body
    print()
    mail.send(msg)
    return

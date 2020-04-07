from flask import Blueprint, render_template, url_for, redirect, flash, Markup, session
from flaskblog import db, sess
from flaskblog.queries.forms import QuerytForm
from flaskblog.models import QueryT, Dictionary
from flaskblog.queries.utils import *
import time
import os
from sqlalchemy import event
from flaskblog import rq
from rq.job import Job
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
        tempterm = form.term.data
        if form.term.data[0] == " ":
            tempterm = form.term.data.strip()
        user_id = session.sid
        potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(tempterm[0])).all()
        qt = get_inp.queue(form.term.data, potential_full, user_id)
        counter =0
        while qt.result != form.term.data and counter <5:
            time.sleep(1)
            print(qt.result)
            print("wait")
            counter = counter +1
        #qt = Job.fetch('form.term.data', rq)
        #print(qt.get_status())
        #c = False
        #while not qt.get_status() == "finished":
        #    time.sleep(0.2)
        #    print(qt.get_status())
        
        flash('Query Successful', 'success')
        return redirect(url_for('main.home'))
         #   check_match(abstracts, term)
    return render_template('create_queryt.html', title='New Query',
                           form=form, legend='New Query')


@queries.route("/egg/<sterm>/<termdata>", methods=['GET'])
def egg(sterm, termdata):
    potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(sterm[0])).all()
    qt = get_inp.queue(sterm, potential_full, termdata)
    counter =0
    while qt.result != form.term.data and counter <5:
        time.sleep(1)
        print(qt.result)
        print("wait")
        counter = counter +1
    
    flash('Your query has been created!', 'success')
    return redirect(url_for('main.home'))


@queries.route("/queryt/<int:queryt_id>")
def queryt(queryt_id):
    queryt = QueryT.query.get_or_404(queryt_id)
    lfmatches = None
    acrmatches = None
    content = queryt.content
    if queryt.lfmatches:
        lfmatches = queryt.lfmatches.split(", ")
    acrreplace = []
    if queryt.acrmatches:
        acrmatches = queryt.acrmatches.split(", ")

        for term in acrmatches:
            termb = "("+term+")"
            if term.lower() == queryt.origterm.lower():
                content = content.replace(termb, '<mark class="acrmatch">' + termb + '</mark>')
            else:
                content = content.replace(termb, '<mark class="acr">'+termb+'</mark>' )
    content = Markup(content)

    return render_template('queryt.html', title=queryt.term, queryt=queryt, lfmatches=lfmatches, acrmatches=acrmatches, content=content)


@rq.job
def get_inp(data, potential_full, user_id, termdata=None):
    time.sleep(0.35)
    search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches = inp(data, potential_full, termdata)
    print("done")
    toot = session.sid
    queryt = QueryT(origterm=search_term, term=fword, content=abstracts, percentmatch=percentmatch,
                    origtermpresent=present, acrmatches=acrmatches, lfmatches=lfmatches, user_id=toot)
    db.session.add(queryt)
    db.session.commit()
    return search_term


from flask import Blueprint, render_template, url_for, redirect, flash, Markup
from flaskblog import db
from flaskblog.queries.forms import QuerytForm
from flaskblog.models import QueryT, Dictionary
from flaskblog.queries.utils import *
import time
import os
from flaskblog import q, r

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
        potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(tempterm[0])).all()
        q.enqueue(get_inp, form.term.data, potential_full)
        
        #for term in fword:
         #   check_match(abstracts, term)
        flash('Your query has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_queryt.html', title='New Query',
                           form=form, legend='New Query')


@queries.route("/egg/<sterm>/<termdata>", methods=['GET'])
def egg(sterm, termdata):
    potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(sterm[0])).all()
    search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches = (inp(sterm, potential_full, termdata))
    addResult(search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches)
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
        # highlightabs = queryt.content.split()
        # x = 0
        # while x < len(highlightabs):
        #     if "(" in highlightabs[x] and ")" in highlightabs[x]:
        #         for term in queryt.acrmatches:
        #             if term in highlightabs[x]:
        #                 (highlightabs[x])
        #                 highlightabs[x] = "<mark>" + highlightabs[x] + "</mark>"
        #     x = x + 1
        # content = highlightabs

    return render_template('queryt.html', title=queryt.term, queryt=queryt, lfmatches=lfmatches, acrmatches=acrmatches, content=content)


def get_inp(data, potential_full, termdata=None):
    time.sleep(10)
    search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches = inp(data, potential_full, termdata)
    queryt = QueryT(origterm=search_term, term=fword, content=abstracts, percentmatch=percentmatch,
                    origtermpresent=present, acrmatches=acrmatches, lfmatches=lfmatches)
    db.session.add(queryt)
    db.session.commit()
    return queryt



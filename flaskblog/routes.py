from flask import render_template, url_for, flash, redirect
from flaskblog import app, db
from flaskblog.forms import QuerytForm
from flaskblog.models import QueryT, Dictionary
from pymed import PubMed
from sqlalchemy import event
from sqlalchemy.event import listen
import sys
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import requests
import json
import subprocess
from os import listdir
from sqlalchemy_utils import functions
import click
import os
db.create_all()

stop_words = stopwords.words('english')
pubmed = PubMed(tool="PubMedSearch", email="maxmoneywells@gmail.com")


@app.route("/")
@app.route("/home")
def home():
    queriest = QueryT.query.all()
    queriest = queriest[::-1]
    tick_file = os.path.join(os.getcwd(), 'flaskblog/static/tick.png')
    #if num matched > 0
    picture_file = "tickg.jpg"
    return render_template('home.html', queriest=queriest, picture_file=picture_file)


@app.route("/about")
def about():
    #run_shelly()
    return render_template('about.html', title='About')


abstract = ""


@app.route("/queriest/new", methods=['GET', 'POST'])
def new_queryt():
    existy = Dictionary.query.filter_by(id=1).first()
    if existy is None:
        def insert_initial_dict():
            print(os.getcwd())
            dict_file = os.path.join(os.getcwd(), 'flaskblog/static/termin.txt')
            fh = open(dict_file)
            for line in fh:
                print(1, existy)
                termo = Dictionary(terminology=line)
                db.session.add(termo)
            db.session.commit()

        insert_initial_dict()
    form = QuerytForm()

    if form.validate_on_submit():
        #terms = get_terms(get_pubmed(form.term.data))
        search_term = form.term.data
        search_term_split = search_term.split()
        enum = 0
        print(search_term_split)
        valid = False
        selected_fullforms = []
        for word in search_term_split:
            print(word)

            if validacr(word):
                potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(word[0])).all()
                fword, valid = checktings(word, potential_full)
                if valid:
                    selected_fullforms.append(fword)
                search_term_split[enum] = fword
            enum = enum + 1

        search_term = " ".join(search_term_split)
        #implement task queue pubmed overload --
        abstracts = get_pubmed(search_term)
        origsearch_term = form.term.data
        #for term in fword:
         #   check_match(abstracts, term)
        queryt = QueryT(origterm=origsearch_term, term=search_term, content=abstracts,percentmatch=1)
        db.session.add(queryt)
        db.session.commit()
        flash('Your query has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_QueryT.html', title='New Query',
                           form=form, legend='New Query')


def checktings(word, potential_full):
    for term in potential_full:
        if word.lower() in term.terminology.lower():
            return word, False
        if findBestLF(word, term.terminology):
            search_term = term.terminology
            return search_term, True
    return word, False


def findBestLF(SF, LF):
    LF = " " + LF
    sIndex = len(SF) - 1

    lIndex = len(LF) - 1

    while (sIndex >= 0):

        currChar = SF[sIndex].lower()
        # print(currChar + " x")
        ##print(LF[lIndex].lower())
        if currChar.isalnum() == True:

            while (lIndex >= 0 and LF[lIndex].lower() != currChar):
                # print(LF[lIndex].lower(),currChar)
                if sIndex == 0 and lIndex > 0:

                    while lIndex > 0:
                        # print(LF[lIndex].lower(),currChar)
                        if (LF[lIndex].lower() == currChar and LF[lIndex - 1] == " "):
                            # print(LF[lIndex:(len(LF))])
                            return LF[lIndex:(len(LF))]

                        lIndex = lIndex - 1

                lIndex = lIndex - 1

        sIndex = sIndex - 1
    return


def validacr(acr):
    x =(any(c.isalpha() for c in acr) and 2 < len(acr) < 10 and (acr[0].isalpha() or acr[0].isdigit()))
    #print("x : " ,x)
    return x


def get_terms(fulltext):
    url = "https://translated-terminology-extraction-v1.p.rapidapi.com/get.php"
    querystring = {"lang": "en", "text": fulltext}
    headers = {
        'x-rapidapi-host': "translated-terminology-extraction-v1.p.rapidapi.com",
        'x-rapidapi-key': "7b04c4070bmshaf8f4632d54293fp13aac9jsnb40fba917447"
    }
    response = requests.get(url, headers=headers, params=querystring)

    return response.json()


def get_pubmed(term):
    results = pubmed.query(term, max_results=5)
    counter = 0
    for article in results:
        abstract = article.abstract
        if abstract is None:
            abstract = "None"
        counter = counter + 1
    return abstract


@app.route("/queryt/<int:queryt_id>")
def queryt(queryt_id):
    queryt = QueryT.query.get_or_404(queryt_id)
    return render_template('queryt.html', title=queryt.term, queryt=queryt)




#def run_shelly():
    #os.chdir(os.getcwd() + "/flaskblog/FlexiTerm-master/script")
    #path = os.getcwd() + "/FlexiTerm.bat"
   # subprocess.call([path], shell=True)
    #subprocess.call([r"C:/Users/mxdba/PycharmProjects/blogflask/flaskblog/FlexiTerm-master/src/FlexiTerm.bat"])
    #os.system("C:/Users/mxdba/PycharmProjects/blogflask/flaskblog/FlexiTerm-master/script/FlexiTerm.bat -1")
    #os.chdir("C:/Users/mxdba/PycharmProjects/blogflask/flaskblog/FlexiTerm-master/src")
    #subprocess.Popen("java -Xmx1000M -cp '..//bin;..//lib//edu.mit.jwi_2.1.5.jar;..//lib//jazzy-core.jar;..//lib//sqlite-jdbc-3.8.11.2.jar;..//lib//stanford-corenlp-2010-11-12.jar;..//lib//stanford-postagger.jar;..//lib//tinylog-1.3.5.jar;..//lib//m3rd_20080611.jar' ../src/FlexiTerm  -1",shell =True,cwd="C://Users//mxdba//PycharmProjects//blogflask//flaskblog//FlexiTerm-master//src")

 #for word in searchTermSplit:
         #   print(word)
        #if checkAcr
        # stringl = ""
        # for key in terms["terms"]:
        #     stringl = stringl , terms["terms"][key]



        #stringl = ""
        #for key in terms["terms"]:
         #   stringl = stringl + " 1 " + key

        # file = "blogflask/flaskblog/FlexiTerm-1.0/text/abstract.txt"
        # print(listdir)
        # with open(file, "w") as file2write:
        #     file2write.write(stringl)


# existy =Dictionary.query.filter_by(id = 0).first()
# print("existy : ",existy)
# if existy is None:
#     def insert_initial_dict():
#         dict_file = os.path.join(app.root_path, '/static/termin.txt')
#         fh = open(dict_file)
#         for line in fh:
#             print("hi" +line)
#             #db.session.add(line)
#         #db.session.commit()
#     insert_initial_dict()


#if not functions.database_exists('sqlite:///site.db'):
    #db.create_all()
    # db.create(Dictionary)
    # db.create_all()
    # dict_file =url_for("static", filename ="termin.txt")
    # fh = open(dict_file)
    # for line in fh:
    #     print(line)
    #     #db.session.add(line)
    # #db.session.commit()
    # fh.close()

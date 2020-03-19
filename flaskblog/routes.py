from flask import render_template, url_for, flash, redirect
from flaskblog import app, db
from flaskblog.forms import QuerytForm
from flaskblog.models import QueryT, Dictionary
from pymed import PubMed
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import requests
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


@app.route("/queriest/new", methods=['GET', 'POST'])
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
        inp(form.term.data)
        #for term in fword:
         #   check_match(abstracts, term)
        return redirect(url_for('home'))
    return render_template('create_QueryT.html', title='New Query',
                           form=form, legend='New Query')


@app.route("/egg/<sterm>/<termdata>", methods=['GET'])
def egg(sterm, termdata):
    inp(sterm, termdata)
    return redirect(url_for('home'))


def inp(termdata, oterm=None):
    search_term = termdata
    search_term_split = search_term.split()
    enum = 0
    present = False
    valid = False
    acrmatches = None
    lfmatches = None
    percentmatch = "N/A"
    fword = search_term
    if len(search_term_split) < 2 and validacr(search_term):
        potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(search_term[0])).all()
        #print(potential_full)

        fword, valid, lfmatches = checktings(search_term, potential_full)
        if oterm:
            fword = oterm
        if lfmatches:
            lfmatches = ", ".join(lfmatches)

        abstracts = get_pubmed(fword)
        #print("valid",valid)

    else:
        abstracts = get_pubmed(search_term)
        #print("invalid")

    # for word in search_term_split:
    #     print(word)
    #
    #     if validacr(word):
    #         potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(word[0])).all()
    #         fword, valid = checktings(word, potential_full)
    #         if valid:
    #             selected_fullforms.append(fword)
    #
    #         search_term_split[enum] = fword
    #     enum = enum + 1

    # implement task queue pubmed overload --
    # abstracts = get_pubmed(fword)


    # for sentence in sentences:
    #     tokens = word_tokenize(sentence)
    #     words = [word for word in tokens if word.isalpha() and not word in stop_words]

    if valid:
        sentences = sent_tokenize(abstracts)
        counter = 0
        hits = 0
        acr_hits = []
        acr_miss = []
        for sentence in sentences:

            if " (" in sentence and ")" in sentence:
                # print(sentence)
                # print(extractpairs(sentence, fword))

                counter_temp, misses_temp, hits_temp, acr_list_temp = extractpairs(sentence, fword)
                counter = counter + counter_temp
                hits = hits + hits_temp
                #print(acr_list_temp)
                temp_hits =[]
                acr_miss.extend(misses_temp)
                for word in acr_list_temp:
                    if word.lower() not in temp_hits:
                        acr_hits.append(word)
                for hit in acr_hits:
                        temp_hits.append(hit.lower())
                # acr_hits.extend(acr_list_temp)
                #print(hits, " : ", counter, " : ", acr_hits)
                # percentmatch = ('%.2s' % str(hits / counter * 100))
                if counter > 100:
                    counter = "99+"
                if hits > 100:
                    hits = "99+"
                percentmatch = str(hits) + "/" + str(counter)

        if acr_hits:
            if search_term.lower() in temp_hits:
                present = True
            else:
                present = False
            acrmatches = ", ".join(acr_hits)

    queryt = QueryT(origterm=search_term, term=fword, content=abstracts, percentmatch=percentmatch,
                    origtermpresent=present, acrmatches=acrmatches, lfmatches=lfmatches)
    db.session.add(queryt)
    db.session.commit()
    flash('Your query has been created!', 'success')


def extractpairs(sent, prelong="None"):
    # print(preLong)
    counter = 0
    hits =0
    sterm_list =[]
    hit_list =[]
    while " (" in sent and ")" in sent:
        # try:
        # first open bracket

        popen = sent.index(" (");
        popen = popen + 1
        # print(popen)
        # first closed bracket
        pclose = sent.index(")", popen)
        # invert string before open bracket
        insent = sent[popen::-1]
        # print(inSent)

        # find start of clause by full stop, comma
        # print(inSent)
        cutoff = (findclause(insent))
        # print("min: ",cutoff)
        # subtract it from first open bracket to uninvert
        if cutoff != 0:
            cutoff = popen - cutoff
        # get long form candidate
        lterm = sent[cutoff:popen]
        # print(lterm)
        # print(lterm)
        # get short form candidate
        sterm = sent[popen + 1:pclose]
        # print(sterm)
        while (("(" in sterm[1:]) and (")" in sent[pclose + 1])):
            nextc = sent.index(")", pclose + 1)
            sterm = sent[popen:nextc + 1]
            pclose = nextc
        # print(sterm)

        if (", " in sterm):
            pclose = sterm.index(", ")
            sterm = sterm[:pclose]
            pclose = popen + pclose

        if ("; " in sterm):
            pclose = sterm.index("; ")
            sterm = sterm[:pclose]
            pclose = popen + pclose
        # print(sterm)

        tokensa = word_tokenize(sterm)
        acrw = [acr for acr in tokensa if len(acr) > 1]
        # print("a ",len(lterm))
        tokenst = word_tokenize(lterm)
        termw = [term for term in tokenst if len(term) > 1]

        if len(acrw) > 2 or len(sterm) > len(lterm):
            lterm = sterm
            #print(termw)
            if len(termw)>0:
                sterm = termw[-1]
        # print(sterm)
        # print(lterm)
        a = "()"
        # print(lterm)
        for char in a:
            sterm = sterm.replace(char, "")
            lterm = lterm.replace(char, "")

        if not any(c.isupper() for c in sterm):
            sterm = ""
        if prelong != "None":
            lterm = prelong
        if validacr(sterm):
            lterm = (matchPair(sterm, lterm, prelong))
            counter = counter + 1
            if not lterm == "None":
                hits = hits + 1
                hit_list.append(sterm)
            else:
                sterm_list.append(sterm)

        # print("hi ",lterm, "no ",sterm)
        # return lterm, sterm
        # print(pclose)
        sent = sent[pclose:]

        #print("counter: ", counter, "hits: ", hits)
        #print("Short FORM: ", sterm," & Long :" ,lterm)
        #print("done")
    return counter, sterm_list, hits, hit_list

    # except Exception:
    #    print ("Not applicable")


def findclause(insent):
    if " ." in insent:
        fs = insent.index(" .")
        # print(fs)
        if " ," in insent:
            com = insent.index(" ,")
            # print(com)
            return min(fs, com)
        return fs
    if " ," in insent:
        com = insent.index(" ,")
        return com
    return 0


def matchPair(acr, deff, prelong="None"):
    if len(acr) < 2:
        return "None"

    bestLF = findBestLF(acr, deff,prelong)

    if bestLF is None:
        return "None"

    tokenLF = word_tokenize(bestLF)
    termLF = [term for term in tokenLF if len(term)]
    t = len(termLF)
    c = len(acr)
    i = c - 1

    while i >= 0:
        if acr[i].isalpha() or acr[i].isdigit():
            c = c - 1
        i = i - 1

    if len(bestLF) < len(acr) or acr + " " in bestLF or bestLF[-1] == acr:
        return "None"
    return bestLF


def checktings(word, potential_full):
    match = False
    compmatches = []
    for term in potential_full:
        if word.lower() in term.terminology.lower():
            #print("INSIDEMEAHHH")
            return word, False, None
        if findBestLF(word, term.terminology):
            #print("NOT INSIDE ME AHAH")
            compmatches.append(term.terminology)
            match = True
    if match:
        search_term = compmatches[0]
        return search_term, True, compmatches
    return word, False, None


def findBestLF(SF, LF, prelong="None"):
    LF = " " + LF
    sIndex = len(SF) - 1

    lIndex = len(LF) - 1

    while (sIndex >= 0):

        currChar = SF[sIndex].lower()
        # print(currChar + " x")
        ##print(LF[lIndex].lower())
        if currChar.isalnum():
            lIndex = lIndex - 1
            while lIndex >= 0 and LF[lIndex].lower() != currChar:
                # print(LF[lIndex].lower(),currChar)
                if sIndex == 0 and lIndex > 0:

                    while lIndex > 0:
                        # print(LF[lIndex].lower(),currChar)
                        if LF[lIndex].lower() == currChar and LF[lIndex - 1] == " ":
                            #print(LF[lIndex:(len(LF))], ":", LF[1:])
                            if prelong != "None" and LF[lIndex:(len(LF))] == LF[1:]:
                                return LF[lIndex:(len(LF))]
                            if prelong == "None":
                                return LF[lIndex:(len(LF))]

                        lIndex = lIndex - 1

                lIndex = lIndex - 1

        sIndex = sIndex - 1
    return


def validacr(acr):
    x = (any(c.isalpha() for c in acr) and 2 < len(acr) < 10 and (acr[0].isalpha() or acr[0].isdigit()))
    #print("VALID : ", x, ": ", acr)
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
    abstracts =""
    abstract ="N/A"
    for article in results:
        abstract = article.abstract
        #print(abstract)
        if abstract:
            if abstracts == "":
                abstracts = abstract
            else:
                abstracts = abstracts + "\n\n" + abstract

        counter = counter + 1
    return abstracts


@app.route("/queryt/<int:queryt_id>")
def queryt(queryt_id):
    queryt = QueryT.query.get_or_404(queryt_id)
    lfmatches = None
    acrmatches = None
    if queryt.lfmatches:
        lfmatches = queryt.lfmatches.split(", ")
    if queryt.acrmatches:
        acrmatches = queryt.acrmatches.split(", ")

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






    return render_template('queryt.html', title=queryt.term, queryt=queryt, lfmatches=lfmatches, acrmatches=acrmatches)






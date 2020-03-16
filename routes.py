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

        valid = False
        if len(search_term_split) < 2:
            if validacr(search_term):
                potential_full = Dictionary.query.filter(Dictionary.terminology.startswith(search_term[0])).all()
                fword, valid = checktings(search_term, potential_full)
                abstracts = get_pubmed(fword)

            else:
                fword = search_term
                abstracts = get_pubmed(search_term)

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

        #implement task queue pubmed overload --
        #abstracts = get_pubmed(fword)

        sentences = sent_tokenize(abstracts)
        # for sentence in sentences:
        #     tokens = word_tokenize(sentence)
        #     words = [word for word in tokens if word.isalpha() and not word in stop_words]
        percentmatch = "N/A"
        if valid:
            counter = 0
            hits = 0
            acr_hits = []
            for sentence in sentences:

                if "(" in sentence and ")" in sentence:
                    #print(sentence)
                    #print(extractpairs(sentence, fword))

                    counter_temp, hits_temp, acr_list_temp = extractpairs(sentence,fword)
                    counter = counter+ counter_temp
                    hits = hits + hits_temp
                    acr_hits.extend(acr_list_temp)
                    print(hits, " : ", counter, " : ", acr_hits)
                    #percentmatch = ('%.2s' % str(hits / counter * 100))
                    if counter > 100:
                        counter = "99+"
                    if hits > 100:
                        hits = "99+"
                    percentmatch = str(hits) + "/" + str(counter)

        #for term in fword:
         #   check_match(abstracts, term)
        queryt = QueryT(origterm=search_term, term=fword, content=abstracts,percentmatch=percentmatch)
        db.session.add(queryt)
        db.session.commit()
        flash('Your query has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_QueryT.html', title='New Query',
                           form=form, legend='New Query')


def extractpairs(sent, prelong="None"):
    # print(preLong)
    counter = 0
    hits =0
    sterm_list =[]
    while "(" in sent:
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
            # print(termw)
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
            lterm = (matchPair(sterm, lterm,prelong))
            if not lterm == "None":
                hits = hits + 1
        # print("hi ",lterm, "no ",sterm)
        # return lterm, sterm
        # print(pclose)
        sent = sent[pclose:]
        counter = counter + 1
        print("counter: ", counter, "hits: ", hits)
        print("Short FORM: ", sterm," & Long :" ,lterm)
        sterm_list.append(sterm)
        print("done")
    return counter, hits, sterm_list

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
    for term in potential_full:
        if word.lower() in term.terminology.lower():
            return word, False
        if findBestLF(word, term.terminology):
            search_term = term.terminology
            return search_term, True
    return word, False


def findBestLF(SF, LF, prelong="None"):
    LF = " " + LF
    sIndex = len(SF) - 1

    lIndex = len(LF) - 1

    while (sIndex >= 0):

        currChar = SF[sIndex].lower()
        # print(currChar + " x")
        ##print(LF[lIndex].lower())
        if currChar.isalnum():

            while lIndex >= 0 and LF[lIndex].lower() != currChar:
                # print(LF[lIndex].lower(),currChar)
                if sIndex == 0 and lIndex > 0:

                    while lIndex > 0:
                        # print(LF[lIndex].lower(),currChar)
                        if LF[lIndex].lower() == currChar and LF[lIndex - 1] == " ":
                            print(LF[lIndex:(len(LF))], ":", LF[1:])
                            if prelong != "None" and LF[lIndex:(len(LF))] == LF[1:]:
                                return LF[lIndex:(len(LF))]
                            if prelong == "None":
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
    abstracts =""
    abstract ="N/A"
    for article in results:
        abstract = article.abstract
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

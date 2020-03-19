from pymed import PubMed
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import requests

stop_words = stopwords.words('english')
pubmed = PubMed(tool="PubMedSearch", email="maxmoneywells@gmail.com")


def inp(search_term, potential_full, oterm=None):
    search_term_split = search_term.split()
    enum = 0
    present = False
    valid = False
    acrmatches = None
    lfmatches = None
    percentmatch = "N/A"
    fword = search_term
    print(search_term_split)
    print(validacr(search_term))
    if len(search_term_split) < 2 and validacr(search_term):
        search_term = search_term.replace(" ", "")
        #print(potential_full)
        print(search_term)
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
        temp_hits = []
        for sentence in sentences:

            if " (" in sentence and ")" in sentence:
                # print(sentence)
                # print(extractpairs(sentence, fword))

                counter_temp, misses_temp, hits_temp, acr_list_temp = extractpairs(sentence, fword)
                counter = counter + counter_temp
                hits = hits + hits_temp
                #print(acr_list_temp)

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
    return search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches



def extractpairs(sent, prelong="None"):
    # print(preLong)
    counter = 0
    hits =0
    sterm_list =[]
    hit_list =[]
    while " (" in sent and ")" in sent[sent.index(" ("):]:
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

    bestLF = findbestlf(acr, deff,prelong)

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
    print(word,potential_full)
    for term in potential_full:
        if word.lower() in term.terminology.lower():
            print("INSIDEMEAHHH")
            return word, False, None
        if findbestlf(word, term.terminology):
            print("NOT INSIDE ME AHAH")
            compmatches.append(term.terminology)
            match = True
    if match:
        search_term = compmatches[0]
        print("xxx",search_term)
        return search_term, True, compmatches
    return word, False, None


def findbestlf(SF, LF, prelong="None"):
    LF = " " + LF
    sIndex = len(SF) - 1

    lIndex = len(LF) - 1
    print(SF,LF,prelong)
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
    x = (any(c.isalpha() for c in acr) and 2 < len(acr) < 10 and (acr[0] == " " or acr[0].isalpha() or acr[0].isdigit()))
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

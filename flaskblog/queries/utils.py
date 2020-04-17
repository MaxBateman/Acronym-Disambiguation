from pymed import PubMed
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import requests

stop_words = stopwords.words('english')
pubmed = PubMed(tool="PubMedSearch", email="maxmoneywells@gmail.com")


#takes search from form, or from "other potential full form"
#if from form selected_full=none, from list= selected full form
def inp(search_term, potential_full, selected_full=None):

    search_term_split = search_term.split()
    present = False
    valid = False
    acrmatches = None
    lfmatches = None
    percentmatch = "N/A"
    fword = search_term
    print(search_term_split)
    print(validacr(search_term))

    #if less than two words and considered an acronym
    if len(search_term_split) < 2 and validacr(search_term):
        search_term = search_term.replace(" ", "")
        #print(potential_full)
        print(search_term)
        #compare search term to dictionary using S&H to get full form, if valid full form found, list of potential full forms
        fword, valid, lfmatches = compare_2_dict(search_term, potential_full)
        #if selected_full not None, replace selected full form with selected_full
        if selected_full:
            fword = selected_full

        #if list of potential full forms populated, join to string
        if lfmatches:
            lfmatches = ", ".join(lfmatches)

        #get abstracts from pubmed
        abstracts, results = get_pubmed(fword)
        #print("valid",valid)

    #not an acronym, just get abstracts
    else:
        #abstracts = get_pubmed(search_term)
        failure = True
        #print("invalid")

    # if term found from dictionary
    if valid:
        sentences = sent_tokenize(abstracts)
        counter = 0
        hits = 0
        acr_hits = []
        acr_miss = []
        temp_hits = []
        #iterate through sentences containing brackets
        for sentence in sentences:

            if " (" in sentence and ")" in sentence:
                # print(sentence)
                # print(extractpairs(sentence, fword))
                # get number of acronyms detected, acronyms that dont match, number of acronyms that match, acronyms that match
                counter_temp, misses_temp, hits_temp, acr_list_temp = extractpairs(sentence, fword)
                counter = counter + counter_temp
                hits = hits + hits_temp
                #print(acr_list_temp)

                acr_miss.extend(misses_temp)
                #for acronym that matched in sentence, appened to global list
                for word in acr_list_temp:
                    if word.lower() not in temp_hits:
                        acr_hits.append(word)
                for hit in acr_hits:
                    temp_hits.append(hit.lower())
                # acr_hits.extend(acr_list_temp)
                #print(hits, " : ", counter, " : ", acr_hits)
                # percentmatch = ('%.2s' % str(hits / counter * 100))
                #if above 99, give range
                if counter > 99:
                    counter = "99+"
                if hits > 99:
                    hits = "99+"
                # number of matching acronyms / total acronyms found
                percentmatch = str(hits) + "/" + str(counter)

        #if original search term in matching acronyms, present true
        if acr_hits:
            if search_term.lower() in temp_hits:
                present = True
            else:
                present = False

            acrmatches = ", ".join(acr_hits)

    if not valid or failure or len(abstracts) < 201:
        failed = True
        search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches = "None"
    else:
        failed = False
    #return db parameters
    return search_term, fword, abstracts, percentmatch, present, acrmatches, lfmatches, failed



def extractpairs(sent, prelong="None"):
    # prelong is dictionary term, or from list which replaces long forms in pair
    counter = 0
    hits =0
    sterm_list =[]
    hit_list =[]
    # while open close brackets still in rest of sentence
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
        # look for nested brackets
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
            if len(termw)>0:
                sterm = termw[-1]
        # print(sterm)
        # print(lterm)
        a = "()"
        # print(lterm)
        # remove brackets
        for char in a:
            sterm = sterm.replace(char, "")
            lterm = lterm.replace(char, "")
        # if no upper case letter not valid
        if not any(c.isupper() for c in sterm):
            sterm = ""
        # if predefined full form, replace detected long form from long short pair with prelong
        if prelong != "None":
            lterm = prelong

        if validacr(sterm):
        	# find potential match long form for long / short pair S&H algorithm
        	# if prelong included best match for long form must be equivalent to prelong
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

#fins clause
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

	#if valid acronym
    if len(acr) < 2:
        return "None"
    #find best long form for acronym
    #if prelong included best long form must be equivalent to prelong
    bestLF = findbestlf(acr, deff,prelong)

    if bestLF is None:
        return "None"

    tokenLF = word_tokenize(bestLF)
    termLF = [term for term in tokenLF if len(term)]
    t = len(termLF)
    c = len(acr)
    i = c - 1
    #length of acronym excluded symbols etc
    while i >= 0:
        if not acr[i].isalpha() or acr[i].isdigit():
            c = c - 1
        i = i - 1

    if len(bestLF) < len(acr) or acr + " " in bestLF or bestLF[-1] == acr or t>2*c or t>c+5 or c>10:
        return "None"

    return bestLF


def compare_2_dict(word, potential_full):

    match = False
    compmatches = []
    print(word,potential_full)
    # for term in dictionary
    for term in potential_full:
    	# if search acronym in term, return acronym(considered as term itself)
        if word.lower() in term.terminology.lower():
            return word, False, None
        # if best long form returned sucessfully, term matches acronym
        if findbestlf(word, term.terminology):
            compmatches.append(term.terminology)
            match = True

    if match:
    	# returns first found match as full form, returns all as a list
        search_term = compmatches[0]
        return search_term, True, compmatches

    return word, False, None


def findbestlf(SF, LF, prelong="None"):

    LF = " " + LF
    sIndex = len(SF) - 1
    lIndex = len(LF)
    print(SF,LF,prelong)
    #iterates through characters in acronym
    while (sIndex >= 0):
        currChar = SF[sIndex].lower()
        #if character is alpha numeric
        if currChar.isalnum():
        	# iterate through long form and compare
            lIndex = lIndex - 1
            # if they match go to next character in short form
            while lIndex >= 0 and LF[lIndex].lower() != currChar:
                # print(LF[lIndex].lower(),currChar)
                if sIndex == 0 and lIndex > 0:
                	# when first character of short form reached
                    while lIndex > 0:
                        # iterate through long form until matching character found preceeded by a space
                        if LF[lIndex].lower() == currChar and LF[lIndex - 1] == " ":
                            # with a prelong best long form must be equivalent to prelong
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
    abstract = "N/A"
    resultlist = []
    for article in results:
        abstract = article.abstract
        #print(abstract)
        if abstract:
            if abstracts == "":
                abstracts = abstract
            else:
            	# formats abstracts
                abstracts = abstracts + "\n\n" + abstract
            resultlist.append(article)

        counter = counter + 1

    return abstracts, resultlist

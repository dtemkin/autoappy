'''
@author: Dan Temkin
@email: 

'''
import spacy
import re
from mcjobs.utils import fullpath
from math import log
from abc import ABCMeta
import string
from time import time
from collections import OrderedDict, namedtuple

try:
    import html
except ImportError:
    from HTMLParser import HTMLParser as html


nlp = spacy.en.English()


class Document(metaclass=ABCMeta):
    def __init__(self):
        self.type = None
        self.text = None
        self._id = None
        self.part = None
        self.parts = None

    @property
    def docid(self):
        return self._id

    @property
    def docparts(self):
        return dict(self.parts)

    @property
    def doctext(self):
        return self.text

    @property
    def doctype(self):
        return self.type

    @property
    def docpart(self):
        return self.part


class Text(Document):


    def __init__(self, text):
        super().__init__()
        self.text = text

    @classmethod
    def xsplit(self, x):
        ## xsplit algorithm adapted from StackOverflow solution provided by: Generic Human
        ## User Profile: http://stackoverflow.com/users/1515832/generic-human
        ## Response: http://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words
        
        
        words = open(fullpath("../docs/words-by-frequency.txt"), mode="r").read().split()
        wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
        maxword = max(len(w) for w in words)

        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
            return min((c + wordcost.get(x[i-k-1:i], 9e999), k+1) for k,c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1,len(x)+1):
            c,k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(x)
        while i>0:
            c,k = best_match(i)
            assert c == cost[i]
            out.append(x[i-k:i])
            i -= k
        return list(reversed(out))

    @classmethod
    def is_stop(self, x, stopsfile=fullpath("../docs/keywords/stops/285-words.ls"), incl_geo=True):
        stops = open(stopsfile, mode="r", newline="\n")
        geostops = open(fullpath("../docs/keywords/stops/usgeo.ls"), mode="r", newline="\n")
        if str(x).lower() in [s.lower() for s in stops]:
            return True
        elif incl_geo is True and str(x).lower() in [g.lower() for g in geostops]:
            return True
        elif 10 < len(str(x).lower()) < 3:
            return True
        else:
            return False

    @classmethod
    def in_dictionary(self, j):
        ws = open(fullpath("../docs/keywords/master_dict.ls"), mode="r", newline="\n")
        if str(j).lower() in [w.lower() for w in ws]:
            return str(j)
        else:
            return None

    def _wash_me(self, text):
        text = html.unescape(text)
        text = text.strip()
        text = text.rstrip()


        text = text.lower()
        cleanr = re.compile('(<.*?>)')

        flashcalls = re.compile('<p>.*?\s..201c+\S.*/p>')
        hiddenchars = re.compile('&[a-z]*?;')

        text = re.sub(flashcalls, "", text)
        text = re.sub(cleanr, '', text)
        text = re.sub(hiddenchars, '', text)
        text = re.sub("\u2028", "", text)
        text = re.sub("\u2019", "", text)
        text = re.sub("\u2014", " ", text)
        text = re.sub("\u00a0", "", text)
        text = re.sub("\n\n", "", text)
        text = re.sub("\n", "", text)
        text = re.sub("•", "\n", text)
        text = re.sub("&", " and ", text)
        text = re.sub("\xa0", "", text)
        text = re.sub("/", "", text)
        text = re.sub("\r\n", " ", text)
        text = re.sub("\(", "", text)
        text = re.sub("\)", "", text)
        text = re.sub("i\.e\.", " like ", text)
        text = re.sub("jr", "junior", text, re.IGNORECASE)
        text = re.sub("jr.", "junior", text, re.IGNORECASE)
        text = re.sub("sr", "senior", text, re.IGNORECASE)
        text = re.sub("sr.", "senior", text, re.IGNORECASE)
        text = re.sub("'\'", "", text)

        return text


    @classmethod
    def token_filter(self, token):

        if self.is_stop(x=token.lower()) is True or int(token.lower().find(".")) > -1:
            return None
        elif len(token) < 3:
            w = self.in_dictionary(j=token)
            if w is not None:
                return w
            else:
                return None


    @property
    def sents(self):
        tlines_START = time()
        doc = nlp(self.doctext)
        lines = []
        li = [sent.string.strip() for sent in doc.sents]
        print("Sent Tokenizer took %s seconds" % (round(time() - tlines_START, 2)))
        for l in li:
            lines.append(self._wash_me(l))
        return lines

    @property
    def keywords(self):
        doc = nlp(self._wash_me(self.doctext))
        props = []
        for w in range(len(doc)):
            if doc[w].pos_ in ["DET","CONJ","ADP","X","PRON","PRP","SPACE","PUNCT"]:
                pass
            elif doc[w].tag_ in ["PRP$"]:
                pass
            elif doc[w].string.strip() in list(string.digits + string.punctuation + string.whitespace):
                pass
            elif self.is_stop(x=doc[w].string.strip()) is True:
                pass
            else:
                token_props = {}.fromkeys(["_id", "token", "tokenlc", "ortho", "clusterID", "log_prob", "lemma", "tag", "pos"])
                token_props["_id"] = w
                token_props["token"] = doc[w].string.strip()
                token_props["tokenlc"] = doc[w].lower_.strip()
                token_props["ortho"] = doc[w].orth_
                token_props["clusterID"] = doc[w].cluster
                token_props["log_prob"] = doc[w].prob
                token_props["tag"] = doc[w].tag_
                token_props["lemma"] = doc[w].lemma_
                token_props["pos"] = doc[w].pos_
                props.append(token_props)
        return props

    def __call__(self):
        return self._wash_me(self.doctext)



















class Elements(Text):
    def __init__(self, textblok, allow_overlap=True):

        super(Elements, self).__init__(textblok)

        self.altsMap = {
            0: ["requirements", "required", "require", "qualifications",
                "necessary", "must", "prerequisite", "requisite",
                "essential", "req"],
            1: ["description", "desc", "descript", "overview",
                "summary", "duties", "role", "responsibilities",
                "what you will", "what you'll"]
            }
        self.xtra = []
        self.segments_dict = {}
        self.text = str(textblok)
        self.overlap = allow_overlap

    def _start_position(self, pt):

        if pt > 30:
            self.xtra.append(self.text[0:pt - 1])
            return pt
        elif pt < 30:
            return 0
        elif pt > len(self.text):
            print("Invalid start point, exceeds number of characters in text string")
        else:
            spos = str(self.text).lower().find(str(pt).lower())
            return spos

    def _stop_position(self, pt):

        if len(self.text) - pt > 30:
            self.xtra.append(self.text[pt + 1: len(self.text)])
            return pt
        elif len(self.text) - pt < 30:
            return len(self.text)
        elif pt > len(self.text):
            print("Invalid end point, exceeds number of characters in text string")
        else:
            epos = str(self.text).lower().find(str(pt).lower())
            return epos

    def keyTagger(self, name, text, firstkey=None, stopkey=None,
                  altstarts=list(), altstops=list()):
        first_start, first_stop = None, None
        startpos, endpos = None, None
        etags, stags = None, None
        ALT, ALTe = list(), list()
        if firstkey in self.altsMap[1]:
            ALT = self.altsMap[1].extend(altstarts)
            ALT.remove(firstkey)
            first_start = firstkey

            stags = OrderedDict({}.fromkeys(range(len(ALT))), ALT)

        elif firstkey not in self.altsMap[1]:
            ALT = self.altsMap[1].extend(altstarts)
            stags = OrderedDict({}.fromkeys(range(len(ALT))), ALT)
            if type(firstkey) is int:
                startpos = self._start_position(pt=firstkey)
            elif type(firstkey) is str:
                first_start = firstkey
            else:
                first_start = stags[0]
                del stags[0]

        if stopkey in self.altsMap[0]:
            self.altsMap[0].remove(stopkey)
            ALTe = self.altsMap[1].extend(altstops)
            first_stop = stopkey

            etags = OrderedDict({}.fromkeys(range(len(ALTe)), ALTe))

        elif stopkey not in self.altsMap[0]:
            ALTe = self.altsMap[0].extend(altstops)
            etags = OrderedDict({}.fromkeys(range(len(ALTe)), ALTe))
            if type(stopkey) is int:
                endpos = self._stop_position(pt=stopkey)
            elif type(stopkey) is str:
                first_stop = stopkey
            else:
                first_stop = etags[0]
                del etags[0]

        if startpos is not None:
            pass
        else:
            if self._start_position(first_start) == -1:
                for s in [k for k in stags.keys()]:
                    if self._start_position(stags[s]) == -1:
                        pass
                        print("Tag %s Not Found" % stags[s])
                    else:
                        startpos = self._start_position(stags[s])
            else:
                startpos = self._start_position(first_start)

        if endpos is not None:
            pass
        else:
            if self._stop_position(first_stop) == -1:
                for e in [k for k in etags.keys()]:
                    if self._stop_position(etags[e]) == -1:
                        pass
                        print("Tag %s Not Found" % etags[e])
                    else:
                        endpos = self._stop_position(etags[e])
            else:
                endpos = self._stop_position(first_stop)

        self.segments_dict.update({name: self.text[startpos:endpos]})
        if self.overlap is False:
            self.text.replace(str(self.segments_dict[name]), "")
        else:
            pass
        if name == "unclassified":
            self._add_unclassified()
        else:
            pass

    def _add_unclassified(self, bind_char=", "):
        if len(self.xtra) > 1:
            x = bind_char.join(self.xtra)
        elif len(self.xtra) == 1:
            x = self.xtra[0]
        else:
            x = ""

        self.segments_dict.update({"unclassified": x})

    def posTagger(self, segments, text):
        '''
        This function attempts to build segments based on the similarity of
        parts of speech ordering in tokenized sentences. The algorithm gets
        progressively more lenient until the number of segments designated is reached.

        Then once the number of segments has been established an initial pass
        tries to locate the segment_name within each of the tokenized segments.
        If the name and/or short name is not found, the function
        will assign the segment_name a part of speech tag and attempt to
        match it to a string in each line selecting the line closest to the top.

        :params segments: str, list of strs or list of tuples
            :::
            Allows user to specify names to use in segment_name
            identification that are not the segment name
            e.g. if a segment_name is "superduper" due to
            potential errors in sentence tokenization
            using the value "supe" to find the
            segment identifier binding. the function will also
            attempt to replace the found string "supe" with the
            segment name,
            iff the locate arg is contained within the segment name,
                the extra characters in the segment name not in the locate arg can be found as
                  a separate element in one of the lines of any segment.
                the locate arg is itself a distinct element in the segment.

            FORMAT: [(str(name_1), str(locate_1)),
                     (str(name_2), str(locate_2)),
                     (str(name_3), )] # The last tuple uses the name arg as the locate parameter

            :::
        :return:
        '''

        print("WARNING! Experimental!")
        segids = {"names": [], "locates": [], "locate_in_name": []}
        if type(segments) is str or int or float:
            segids["names"].append(segments)
            segids["locates"].append(segments)
            segids["locate_in_name"].append(True)
        else:
            for i in range(len(segments)):
                if type(segments[i]) is tuple or list:
                    if len(segments[i]) == 2:
                        segids["names"].append(str(segments[i][0]))
                        segids["locates"].append(str(segments[i][1]))
                        if str(segments[i][0]).find(str(segments[i][1])) > -1:
                            segids["locate_in_name"].append(True)
                        else:
                            segids["locate_in_name"].append(False)
                    elif len(segments[i]) == 1:
                        if segments[i][0] == None:
                            segids["names"].append(str(segments[i][1]))
                            segids["locates"].append(str(segments[i][1]))
                            segids["locate_in_name"].append(True)
                        elif segments[i][1] == None:
                            segids["names"].append(str(segments[i][0]))
                            segids["locates"].append(str(segments[i][0]))
                            segids["locate_in_name"].append(True)
                    else:
                        print("invalid number of segment parameters")
                elif type(segments[i]) is str or int or float:
                    segids["names"].append(str(segments[i]))
                    segids["locates"].append(str(segments[i]))

    def partition(self, doctext):
        doc = nlp(doctext)
        doclines = [sent.string.strip() for sent in doc.sents]
        docprops = []

        for i in range(len(doclines)):
            line = OrderedDict(
                {}.fromkeys(["lineid", "linetext", "kwdslst", "kwdpos", "kwdprops", "segment_name", "segment_id"]))

            line["lineid"] = i
            line["linetext"] = doclines[i]

            l = nlp(line["linetext"])
            liwds = [sent.string.strip() for sent in l]

            line["kwdslst"] = liwds
            props = []
            kwdpos = {}.fromkeys(("kwd", "coarse", "fine",), [])
            for w in range(len(liwds)):
                postag = namedtuple("tagprops", ["docid", "kwd", "kwd_logprob", "fine_pos", "coarse_pos", "lineidx",
                                                 "brown_clustid" "deptree", "orth_props"])
                kwdpos["kwd"].append(liwds[w].text), kwdpos["coarse"].append(liwds[w].pos_), kwdpos["fine"].append(
                    liwds[w].tag_)

                props.append(postag(i, liwds[w].text, liwds[w].prob, liwds[w].tag_, liwds[w].pos_, w, liwds[w].cluster,
                                    liwds[w].subtree, liwds[w].orth_))
            line["kwdprops"] = props
            line["kwdpos"] = kwdpos
            docprops.append(line)

    def compare_docs(self, doc0, doc1):
        pass

    def regexTagger(self, name, start_pattern, end_pattern):
        pass

    def __dict__(self):
        return self.segments_dict



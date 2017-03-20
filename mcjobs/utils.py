import os
import time
import json 
from math import log
import spacy
import re
from collections import OrderedDict, namedtuple
try:
    import html
except ImportError:
    from HTMLParser import HTMLParser as html


def fullpath(x):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), x))

def getids():
    return [i for i in range(round(time.time()*100, 0))]

def getConfig(cfgfile, srcname):
    try:
        j = json.load(fullpath(cfgfile), encoding="utf-8")
    except IOError as err:
        print("Failed to read file")
    else:
        try:
            conf = j["config"][srcname]
        except ValueError as err:
            print("Invalid Key: %s " % srcname)
        else:
            return conf

##
##def ProcessText(object):
##
##    def __init__(self, textdocs, doc_group, lang="English"):
##        self.nlp = spacy.load(lang[:1].lower())
##        self.texts = []
##        self.group = doc_group
##        for textdoc in textdocs:
##            self.texts.append(self.nlp.make_doc(textdoc))
##
##    def pipeline(self, doc):
##        tags = self.nlp.tagger(doc)
##        parsedeps = self.nlp.parser(doc)
##        ents = self.nlp.entity(doc)
##
##
##
##    def lines(self, doc, _id):
##        sent = namedtuple(".".join([str(self.group), str(_id)]), ["lineid", "linetxt"])
##
##
##        return [sent(linenum, doc.sents[linenum]) for linenum in range(len(doc.sents))]
##
##
##    def kwds(self, line):
##        li = self.nlp.tokenizer(line.linetxt)
##
##        kwds = [(wordid, li[wordid].string.strip()) for wordid in range(len(li))]
##
##
##        tags = self.nlp.tagger(kwds)
##        parsedeps = self.nlp.parser(kwds)
##
##        kwd = namedtuple(".".join([str(line.lineid), i]), ["kwdid","kwdtxt","pos_coarse", "pos_fine", "deptree", "kwd_ancestors"])
##        pass
##        # return [kwd(i, li[i].text, li[i].tag_, li[i].pos_, li[i].      for i in range(len(li))
##
##    def __call__(self):
##        i = 0
##
##        for rawdoc in self.nlp.pipe(self.texts, batch_size=10000, n_threads=3):
##            doc = self.nlp.tokenizer(rawdoc)
##            docid = i
##
##


    



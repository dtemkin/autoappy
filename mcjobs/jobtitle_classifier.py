'''
@author: Dan Temkin
@email: 

'''
import pymongo
from mcjobs.utils import fullpath
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.metrics import accuracy_score
from nltk.corpus import stopwords
import string
import re
labels = ["Data Analyst", "Data Scientist",
          "Database Administrator", "Business Analyst"]


def jobsdata(database, collection, **connkwargs):
    host = connkwargs.get("host", "127.0.0.1")
    port = connkwargs.get("port", 27017)

    client = pymongo.MongoClient(host=host, port=port)
    db = client[database]
    coll = db.get_collection(collection)
    resp = dict(coll.find())
    print(resp)


def parse_examples(cls):
    fmttitle = "+".join([x.lower() for x in cls.split(" ")])
    cls_words = []
    file = fullpath("../docs/jobpost-examples/keywords/by-title/%s.ls" %  fmttitle)
    with open(file, mode="r") as file:
        readr = csv.reader(file)
        for row in readr:
            words = row.split(" ")
            cls_words.extend([w.lower() for w in words])
        file.close()
    return cls_words

def counts(classifier, dct):
    kwd_counts = {}
    data = dict(filter(lambda x: x==classifier, dct["jobtitle"]))
    for d in data:
        for k, v in d["kwd_counts"]:
            if k in [key for key in kwd_counts.keys()]:
                kwd_counts[k] += v
            else:
                kwd_counts.update(dict(k=v))
    return kwd_counts

d = jobsdata("jobData", "jobposts")
print(d)
for c in classes:
    ex = parse_examples(c)
    cnt = counts(c, d)
    ndiffs = len(set(ex).difference(set([k for k in cnt.keys()])))
    print(ndiffs)


class Classifier(object):

    def __init__(self, textsegments):
        pass












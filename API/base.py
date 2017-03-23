'''
Created on Dec 12, 2016

@author: dysmas
'''
from abc import abstractmethod
import pymongo
from mcjobs.utils import fullpath
from queue import Queue
import yaml
import threading
import spacy
import re
import requests

nlp = spacy.load("en")
class Filters(object):

    def __init__(self, datadict):
        self.datadict = datadict

    def mgmt(self):
        mgmtkeywords = ["supervisor", "manager", "senior", "sr.",
                        "sr", "coordinator", "leader", "lead",
                        'ii', 'iii', '3', '2', "partner", "associate",
                        "director", "president", "head",
                        "chief", "executive","mgr","technician"]
        y = 0
        for mgmt_word in mgmtkeywords:

            if self.datadict["jobtitle"].lower().find(mgmt_word, 0, len(self.datadict["jobtitle"])) > -1:
                y += 1
            else:
                pass

        if y > 0:
            return False
        else:
            return True


    def recruiters(self):
        recruiters = ["robert half", "apex", "kelly mitchell",
                      "staffing", "vincentbenjamin","collabera",
                      "nigel frank","confidential","ashley ellis",
                      "resources","washington frank","careers",
                      "solutions","hirelive","hire","job",
                      "employment","group","modis","century",
                      "ableforce","mason frank","service",
                      "kforce","adecco","staff"]
        x = 0
        for recruiter_word in recruiters:
            r = re.compile(recruiter_word)
            if r.search(self.datadict["company"].lower()) > -1:
                x += 1
            else:
                pass

        if x > 0:
            return False
        else:
            return True

    def title(self, title_strings, partial=True):
        t = 0
        if self.datadict["jobtitle"].lower().find(title_strings.replace("+", " ").lower(), 0, len(self.datadict["jobtitle"])) > -1:
            return True
        elif partial is True:
            strings = title_strings.split("+")

            for s in strings:
                if self.datadict["jobtitle"].lower().find(s.lower()) > -1:
                    t += 1
                else:
                    pass
            if t > 1:
                return True
            else:
                return False

        else:
            return False


class Source:
    '''
    Initialize Source Base Class
    '''

    def __init__(self):
        '''
        ##############
        # Parameters #
        ##############

        srcname : str
            Accepts = "indeed","careerbuilder","glassdoor","linkedin"
        '''
        super(Source, self).__init__()
        self.source = None
        self.rawtext = None
        self.endpoint = None
        self.apitype = None
        self.queue = Queue()

    @property
    def head(self):
        return self.config["common"]["request"]["headers"]

    @property
    def authdict(self):
        return self.config["source"][self.__name__]["auth"]

    @property
    def config(self):
        stream = open(fullpath("apiconfig.yml"), mode="r")
        conf = yaml.load(stream=stream)
        return conf

    @property
    def __name__(self):
        return self.source

    @property
    def url(self):
        return self.config["source"][self.source][self.apitype][self.endpoint]


    def _dupe_check(self, collection, valdict, **connkwargs):
        host, port = connkwargs.get("hosts", "127.0.0.1"), connkwargs.get("port", 27017)
        client = pymongo.MongoClient(host=host, port=port)
        db = client["JobsData-%s" % self.source]
        coll = db[collection]
        if coll.find_one(filter=valdict) is not None:
            return True
        else:
            return False

    # def Save(self, data, **connkwargs):
    #
    #     host, port = connkwargs.get("hosts", "127.0.0.1"), connkwargs.get("port", 27017)
    #     client = pymongo.MongoClient(host=host, port=port)
    #     db = client["JobsData"]
    #     for k in data.keys():
    #         collection = db[self.srcname][k]
    #         if k == "jobsearch":
    #             print("Saving Search Data")
    #
    #             if collection.count() > 0:
    #                 for d in range(len(data[k]["searchresults"])):
    #                     dupe = self._dupe_check(k, {"srcid": data[k]["searchresults"][d]["srcid"]},
    #                                             **connkwargs)
    #                     if dupe is True:
    #                         del data[k]["searchresults"][d]
    #                         print("%s Search Result: %s @ %s Already Exists in Database" % (
    #                         self.srcname, data[k]["searchresults"][d]["JobTitle"],
    #                         data[k]["searchresults"][d]["Company"]))
    #                     else:
    #                         pass
    #             else:
    #                 pass
    #
    #             if len(data[k]["searchresults"]) == 0:
    #                 print("No Search Results to Insert.")
    #             else:
    #                 print("Inserting...")
    #                 collection.insert_one(data[k])
    #             print("Done.")
    #         if k == "jobposts":
    #             checked = []
    #             if collection.count() > 0:
    #                 for d in data[k]:
    #                     dupe = self._dupe_check(k, {"srcid": d["srcid"]}, **connkwargs)
    #                     if dupe is True:
    #                         pass
    #                         print("%s Job: %s @ %s Already Exists in Database" % (
    #                         self.srcname, d["JobTitle"], d["Company"]))
    #                     else:
    #                         checked.append(d)
    #
    #             else:
    #                 checked.extend(data[k])
    #             if len(checked) == 1:
    #                 print("Inserting 1 new post into database...")
    #                 collection.insert_one(checked[0])
    #
    #             elif len(checked) == 0:
    #                 print("No Values to Insert.")
    #             else:
    #                 print("Inserting %s new posts into database..." % len(checked))
    #                 collection.insert_many(checked)
    #
    #             print("Done.")
    #
    # def process_queue(self):
    #     while True:
    #         post = self.jobpost_proc_queue.get()
    #         print("Getting Detail For Job Result %s of %s: %s @ %s" % (
    #         post[1], len(self.searchresults) - 1, self.searchresults[post[1]]["jobtitle"],
    #         self.searchresults[post[1]]["company"]))
    #         self.Post(datadict=post[0], _id=post[1])
    #         self.jobpost_proc_queue.task_done()
    #
    #
    # def run(self, nthreads=8):
    #     for n in range(int(nthreads)):
    #         t = threading.Thread(target=self.process_queue)
    #         t.daemon = True
    #         t.start()
    #
    #     if len(self.searchresults) == 0:
    #         print("Run 'Search' instance for chosen source before calling run")
    #     else:
    #         for i in range(len(self.searchresults)):
    #             self.jobpost_proc_queue.put((self.searchresults[i], i))
    #         self.jobpost_proc_queue.join()
    #
    #     self.Save(data={
    #         self.srcname: {"jobsearch": self.searchdata, "jobposts": self.postdata}
    #         })



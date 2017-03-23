from time import sleep
from urllib.parse import urlencode

import requests

from API.base import Source, Filters
from mcjobs.text.base import Text

x = Source()
x.source = "muse"

request_session = requests.Session()

request_session.headers.update(dict(**x.head))
request_session.headers.update(dict(**x.authdict))


def Search(terms, location, **kwargs):
    '''
    :terms:
    :location:
    :params company:
    :params category:
    :params jobtype:
    :return:
    '''
    x.apitype = "job"
    x.endpoint = "search"
    baseparams = dict(page=0)
    jt = kwargs.get("jobtype")
    cat = kwargs.get("category", ["Data Science"])
    results = []
    params = []


    if type(jt) is str:
        params.append(("level", jt))

    elif type(jt) is list:
        for j in jt:
            params.append(("level", j))


    if type(location) is list:
        for l in location:
            params.append(("location", l))
    else:
        params.append(("location",location))

    if type(cat) is None:
        pass
    elif type(cat) is list:
        for c in cat:
            params.append(("category", c))
    elif type(cat) is str:
        params.append(("category", cat))

    url = "".join([x.url, urlencode(params)])

    req1 = request_session.get(url, params=baseparams, stream=True)
    print(req1.url)
    js = req1.json()
    for g in js["results"]:
        result = fix_results(g)

        Filter = Filters(result)
        if Filter.mgmt() is False:
            pass
        elif Filter.title(title_strings=terms, partial=True) is True:
            results.append(result)


    for i in range(1, js["page_count"]):
        pay = baseparams
        pay.update({"page":i})
        urlx = "".join([x.url, urlencode(params)])

        req2 = request_session.get(urlx, params=pay,  stream=False)
        sleep(0.5)
        jsx = req2.json()

        for h in jsx["results"]:

            resultx = fix_results(h)
            Filter = Filters(resultx)
            if Filter.mgmt() is False:
                pass
            else:
                if Filter.title(title_strings=terms, partial=True) is False:
                    pass
                else:

                    results.append(resultx)
        print(i, "of", js["page_count"])
    return results

def fix_results(d):

    d["levels"] = [d["levels"][u]["name"].lower() for u in range(len(d["levels"]))]
    d.update({"tags":  [d["tags"][u]["name"].lower() for u in range(len(d["tags"]))]})
    d.update({"locations": [d["locations"][u]["name"].lower() for u in range(len(d["locations"]))]})
    d.update({"url":d["refs"]["landing_page"]})
    d.update({"cosrcid":d["company"]["id"]})
    d.update({"company":d["company"]["name"].lower()})
    d.update({"srcid":d["id"]})
    d.update({"categories":[d["categories"][u]["name"] for u in range(len(d["categories"]))]})
    d.update({"jobtitle":d["name"]})
    txt = Text(d["contents"])
    d.update({"contents":txt(), "source":x.source})
    del d["categories"], d["name"], \
        d["locations"], d["id"]

    return d


def Post(datadict, _id):
    x.apitype = "job"
    x.endpoint = "info"
    postdata = []
    print("Getting Post")

    srcurl = "".join([x.url, str(datadict["srcid"])])

    req = request_session.get(srcurl)

    js = req.json()
    data = fix_results(js)
    txt = Text(data["contents"])
    data.update({"contents":txt(), "keywords":txt.keywords, "lines":txt.sents, "source":x.source})
    del data['refs']
    postdata.append(data)
    print("Got post %s" % _id)
    return postdata


def Companies(self):
    x.apitype = "company"
    x.endpoint = "list"
    pass

def Company(self, datadict):
    x.apitype = "company"
    x.endpoint = "info"

    url = "".join([x.config["source"][x.source]["companyurl"], str(datadict["cosrcid"])])
    req = request_session.get(url, stream=False)
    js = req.json()

    js["industries"]= [js["industries"][u]["name"].lower() for u in js["industries"]]
    js["images"] = list(filter(lambda y: y.find("image", 0, len(y))>-1, [js["refs"][k] for k in js["refs"].keys()]))
    js["joblist_url"] = js["refs"]["jobs_page"]
    js["cosize"] = js["size"]["short_name"]

    result = fix_results(js)

    del result["refs"]
    return result




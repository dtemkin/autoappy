from __future__ import unicode_literals, print_function

from datetime import date

import numpy as np
import requests
from bs4 import BeautifulSoup as bsoup

from API.base import Source
from mcjobs.text.base import Text
from mcjobs.utils import fullpath

defaultargs = dict(v=2, format="json", limit=25, fromage=7,
                   radius="50", jt="fulltime", st="employer",
                   filter=1, filterdupes="true", latlong=1,
                   psf="advsrch", as_not="senior+manager+director+sr+mgr+supervisor")
searchdata = {"rundate": date.today().strftime("%Y-%m-%d"), "totalpages": 0}

x = Source()
x.source = "indeed"


request_session = requests.Session()
request_session.headers.update(x.config["common"]["request"]["headers"])
request_session.params.update(x.authdict)

def Search(terms, loc, **params):
    """
    :param params:
    :terms str:
    :loc str:
        format: 'City' or
                'State' or
                'State Abbrev' or
                'City, State'
        Use a postal code or a "city, state/province/region" combination.
    PostAge : int
        Default=7
        Number of days back to search.
    PerPage : int
        Default=10
        Max=50
        Number of results per page to return
    Radius : int
        Default=25
        Max=100
        Distance from search location ("as the crow flies").
    OrderBy : str
        Default='relevance'
        Sort by 'relevance' or 'date'.
    SiteType : str
        To show only jobs from job boards use "jobsite". For jobs from direct employer websites use "employer".
    EmpType : str
        Default="all"
        Allowed values: "fulltime", "parttime", "contract", "internship", "temporary".
    Start : int
        Default=0
        Start results at this result number, beginning with 0.
    limit : int
        Maximum number of results returned per query. Default is 10
    FilterDuplicates : int
        Default=1
        Filter duplicate results. 0 turns off duplicate job filtering.
    ShowLatLong : int
        Default=1
        If latlong=1, returns latitude and longitude information for each job result. Default is 0.
    Country : str
        Default="us"
        Search within country specified. Default is us See below for a complete list of supported countries.
    PayFilter : str
        Filter results by pay "minimum" or "min - max"

    :return: list of dicts
    """
    x.apitype = "job"
    x.endpoint = "search"
    results = []
    pay = dict(**params)

    pay.update({"terms": terms})

    req = request_session.get(x.url, params=_convert_request_kwargs(pay))

    js = dict(req.json())

    searchdata.update(js)
    result = req.json()["results"]
    print("Getting Page ", 0)
    for g in range(len(result)):
        try:
            srcids = [results[r]["srcid"] for r in range(len(results))]
        except KeyError:
            result[g].update({"source": "indeed", "id": g+len(results), "srcid": result[g]["jobkey"]})
            del result[g]["jobkey"]
            results.append(result[x])
        else:
            if result[g]["jobkey"] not in srcids:
                result[g].update({"id": g+len(results), "srcid": result[g]["jobkey"]})
                del result[g]["jobkey"]
                results.append(result[g])
            else:
                pass

    searchdata["totalpages"] += 1
    for i in range(25, int(req.json()["totalResults"]), 25):
        print("Getting Page %s" % (searchdata["totalpages"]))
        pay.update({"Start": i})

        reqx = request_session.get(x.url, params=_convert_request_kwargs(pay))

        resultsx = reqx.json()["results"]

        for y in range(len(resultsx)):
            currsrcids = [results[r]["srcid"] for r in range(len(results))]
            if len(results) == 0 or resultsx[y]["jobkey"] not in currsrcids:
                txt = Text(str(resultsx[y]["snippet"]))
                resultsx[y].update(
                        {"source": x.source, "id": y+len(results), "srcid": resultsx[y]["jobkey"], "snippet": txt()})
                del resultsx[y]["jobkey"]
                del resultsx[y]["onmousedown"]

                results.append(resultsx[y])

            else:
                pass
        searchdata["totalpages"] += 1
    print("Done.")
    return results


def Post(_id, datadict):
    """
    ##############
    # Parameters #
    ##############


    @tag url : str
        Default = None
    """
    x.apitype = "job"
    x.endpoint = "info"
    postdata = []
    print("Working on Post %s) %s @ %s" % (_id, datadict["jobtitle"], datadict["company"]))

    req = request_session.get(datadict["url"])

    truncdict = {"id": _id, "srcid": datadict["srcid"], "source": x.source,
                 "jobtitle": datadict["jobtitle"].replace(".", "-"),
                 "company": datadict["company"].replace(".", "-"),
                 "city": datadict["city"], "state": datadict["state"]}

    soup = bsoup(req.text, "lxml")
    table = soup.find("table", attrs={"id": "job-content"})
    summary = table.find("span", attrs={"id": "job_summary"})
    s = Text(summary.get_text().strip())

    truncdict.update({"summary": s(), "kwds": s.keywords, "lines": s.sents})
    postdata.append(truncdict)
    return postdata

def codes(group, showall=True):
    if group == "country":
        names, code = np.loadtxt(fullpath("../../docs/codelists/indeed/country.codes"),
                                 dtype=np.str, skiprows=1, unpack=True)
        if showall is True:
            for i in range(len(code)):
                print((names[i], code[i]))


def _convert_request_kwargs(kwargs):
    convkwargs = defaultargs
    convdict = {"terms": "q", "loc": "l", "Start": "start",
                "EmpType": "jt", "ShowLatLong": "latlong", "Country": "co",
                "FilterDuplicates": "filterdupes", "SiteType": "st",
                "PayFilter": "salary", "OrderBy": "sort",
                "PerPage": "limit", "Radius": "radius"}

    for key in kwargs.keys():
        try:
            convkwargs.update({convdict[key]: kwargs[key]})
        except KeyError:
            print("%s Key Invalid! Must be one of:\n" % key,
                  [k for k in convdict.keys()])
        else:
            pass
    return convkwargs

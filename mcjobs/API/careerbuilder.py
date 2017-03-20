
from mcjobs.API.base import Source, filter_mgmt, filter_recruiters
from mcjobs.text.base import Text
import json
from datetime import date
import requests


x = Source()
x.source = "careerbuilder"

defaultargs = dict(outputjson="true", PerPage=100, ShowApplyRequirements=True,
                   ShowCategories=True, ShowPayInfo=True, Radius=50)
searchdata = {"rundate": date.today().strftime("%Y-%m-%d"), "source": x.source}


request_session = requests.Session()
request_session.headers.update(x.head)
request_session.params.update(x.authdict)

def _rebuild_search_fields(dct):

    fields_map = {"JobServiceURL":"url", "SimilarJobsURL":"similar_url",
                  "DID":"srcid","CompanyDID":"cosrcid","DescriptionTeaser":"snippet",
                  "JobLevel":"lvl", "PostedDate":"date","PostedTime":"time","LocationLatitude":"lat",
                  "LocationLongitude":"long"}

    d = dict(map(lambda i: (dct[fields_map[i]], dct[i]), [k for k in fields_map.keys()]))
    d.update(dct)
    d.update({"Skills": [n["Skill"] for n in dct["Skills"]]})
    for k in fields_map.keys():
        del d[k]

    return d

def Search(terms, loc, params, typ="JobTitle"):
    '''

    JobTitle : str or list of strings (show jobs with set or similar Job Title)
    Company : str (show only jobs from particular company)
    Skills : str or list of strings (show only jobs with at least one of set skills)
    terms : str or list of strings (show only job posts containing at least one of set keywords)
    Location : str (show jobs in location)
        format: 'City' or
                'State' or
                'State Abbrev' or
                'City, State'
    Radius : int (show only jobs within set distance in miles)
        max=100,
        default=30,
        accepts -- [5,10,15,20,30,50,100]
    PayInfoOnly : bool (show only job payment info)
        default=False
    ShowPayInfo : bool (include pay info in response if provided)
        default=True
    RelocateJobs : bool (show only jobs that offer relocation assistance)
    PayLow : int or float (show only jobs with pay above or at level)
    PayHigh : int or float (show only jobs with pay below or at level)
    ShowApplyRequirements : bool (include application requirements in response)
        default = True
    ShowCategories : bool (include job categories in response)
    EmployeeTypeCode : str
        accepts -- see: mcjobs.source().CodesList("Employee")
    SpokenLanguage : str (show only jobs where language spoken is same as set value and post is in set language)
        default=ENG
    OrderDirection : str
        accepts -- 'desc' or 'asc'
        default = "desc"
    OrderBy : str
        accepts -- Any Job Search Response Field
        default="similarity"
    UrlCompressionService : str (compresses job urls in response using specified service)
        accepts -- bitly or tinyurl]


    NOTE: For full list of API V1, search parameters see Careerbuilder API Docs
    '''
    x.apitype = "job"
    x.endpoint = "search"
    results = []
    pay = params
    pay.update({typ: terms, "Location":loc, "PageNumber":0})
    pay.update(defaultargs)
    req = request_session.get(x.url, params=pay)
    resp = req.json()["ResponseJobSearch"]

    searchdata.update(pay)
    del resp["RequestEvidenceID"]
    searchdata.update(resp)

    result = resp["Results"]["JobSearchResult"]
    if len(result) == 0:
        pass
    else:
        print("Getting Page ", 0)
        for r in range(len(result)):

            result[r].update({"source":x.source,"id":r+len(results),"srcid":result[r]["DID"]})
            result[r]["url"] = result[r]["JobServiceURL"]
            result[r]["coinfo_url"] = result[r]["CompanyDetailsURL"]
            result[r]["cosrcid"] = result[r]["CompanyDID"]

            del result[r]["DID"],result[r]["CompanyDID"], result[r]["JobServiceURL"], result[r]["CompanyDetailsURL"]

            results.append( dict(map(lambda l: (l.lower(), result[r][l]), [k for k in result[r].keys()])))

        for i in range(1, int(resp["TotalPages"])):
            print("Getting Page ", i)
            pay2 = pay
            pay2.update({"PageNumber":i})
            reqx = request_session.get(x.url, params=pay2)
            resultx = reqx.json()["ResponseJobSearch"]["Results"]["JobSearchResult"]
            for j in range(len(resultx)):
                resultx[j]["url"] = resultx[j]["JobServiceURL"]
                resultx[j]["coinfo_url"] = resultx[j]["CompanyDetailsURL"]
                resultx[j]["cosrcid"] = resultx[j]["CompanyDID"]

                resultx[j].update({"source":x.source,"id":j+len(results),"srcid":resultx[j]["DID"]})
                del resultx[j]["DID"], resultx[j]["CompanyDID"], resultx[j]["JobServiceURL"], resultx[j]["CompanyDetailsURL"]
                results.append(dict(map(lambda p: (p.lower(), resultx[j][p]), [k for k in resultx[j].keys()])))
        print("Done.")
    return results

def Post(datadict, _id):
    '''
    ##############
    # Parameters #
    ##############

    *NOTE: Either url or srcid is required. If both are present
           will default to using the url.


    url : str  # REQUIRED*
        Default = None
    '''
    x.apitype = "job"
    x.endpoint = "info"
    print("Working on Post %s) %s @ %s" % (_id, datadict["jobtitle"], datadict["company"]))
    post = {}
    data=[]

    pay = defaultargs

    pay.update({"DID":datadict["srcid"]})
    req = request_session.get(x.url, params=pay)

    js = req.json()
    resp = js["ResponseJob"]["Job"]
    print("Gathering Data...\n\t (%s) - %s @ %s" % (_id, resp["JobTitle"], resp["Company"]))
    # if len(resp["CategoriesCodes"]) > 0 and resp["Categories"] == "":
    #     if type(resp["CategoriesCodes"]) is list:
    #         for code in resp["CategoriesCodes"]:
    #             resp.update({"Categories": _convert_code(group="Category", x=code)})
    #     elif type(resp["CategoriesCodes"]) is str:
    #         resp.update({"Categories": _convert_code(group="Category", x=resp["CategoriesCodes"])})
    # else:
    #     pass
    # if type(resp["IndustryCodes"]) is list:
    #     for code in resp["IndustryCodes"]:
    #         resp.update({"Industries": _convert_code(group="Industry", x=code)})
    # elif type(resp["IndustryCodes"]) is str:
    #     resp.update({"Industries": _convert_code(group="Industry", x=resp["CategoriesCodes"])})
    # else:
    #     pass

    txt = Text(" ".join([resp["JobRequirements"], resp["JobDescription"]]))

    resp.update({"summary":txt(), "tokens": txt.keywords, "lines": txt.sents, "source":x.source})

    del resp["JobRequirements"]
    del resp["JobDescription"]
    post.update(resp)

    post.update({"id":_id})
    p = dict(map(lambda i: (i.lower(), post[i]), [k for k in post.keys()]))
    data.append(p)
    return data


def _convert_code(group, x):
    try:
        refs= Codes(group=group, showall=False)
    except KeyError:
        print("Invalid Group: %s  - Code: %s " % (group, x))

    else:
        tups = list(filter(lambda i: i[i[0] == x],[r for r in refs]))
        names = [tup[1] for tup in tups]
        return names

def Codes(group, showall=True):
    """
    ##############
    # Parameters #
    ##############

    group : str  # REQUIRED
    showAll : bool  # DEFAULT=True

    """

    x.apitype = "job"
    x.endpoint = "codes"

    grpdict = {"Industry":"industrycodes","Education":"education",
               "Category":"categories","Employee":"employeetypes"}

    if group not in grpdict.keys():
        raise KeyError("No Codes Found for Group: %s " % group)
    else:
        url = "".join(["http://api.careerbuilder.com/v1/", grpdict[group]])

        req = requests.get(url)
        js = req.json()
        base = js["Response%sCodes" % group]["%sCodes" % group]["%sCode" % group]
        codes = []
        for n in range(len(base)):

            codes.append((base[n]["Code"], base[n]["Name"]["#text"]))

        if showall is True:
            print(codes)
        else:
            pass

    return codes
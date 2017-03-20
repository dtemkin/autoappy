'''
Created on Jan 20, 2017

@author: dysmas
'''


from mcjobs.utils import fullpath
from mcjobs.API.base import Source
import requests

x = Source()
x.source = "glassdoor"

request_session = requests.Session()
request_session.headers.update(x.head)
request_session.params.update(x.authdict)




def Search(terms, loc, **params):
    '''
    ##############
    # Parameters #
    ##############

    keywords : str or list(str)
    location : str
        Format : City||City, State||State
    age : int
    companyRating : int
        Format : x.x
        Accepts : 0, 1, 2, 3, 4

    jobType : str
        Accepts : "all", "fulltime","parttime","contract","internship"
                  "temporary", "internship", "apprenticeship", "entrylevel"
    radius : int
        Accepts : 0, 5, 10, 15, 25, 50, 100
        (0 == "Exact Location")

    '''

    payload = _fmt_params(dict(**params))
    search = "+".join(terms.split(" "))
    payload.update({"typedKeyword":search, "sc.keyword":search})


    req = request_session.get(x.url, params=payload)

def _fmt_params(kwargs):
    payload = {}
    if kwargs["companyRating"]:
        payload.update({"minRating":str(round(float(kwargs["companyRating"]), 0))})
    if kwargs["age"]:
        payload.update({"fromAge":str(kwargs["age"])})
    if kwargs["jobType"]:
        payload.update({"jobType":kwargs["jobtype"]})
    if kwargs["location"]:
        payload.update({"locKeywords":kwargs["location"]})
    if kwargs["radius"]:
        payload.update({"radius":kwargs["radius"]})
    return payload



def Post(datadict, _id):
    '''
    ##############
    # Parameters #
    ##############

    url : str

    '''

    req = requests.get(datadict["url"])



def Progression(terms, loc, **params):
    '''
    ##############
    # Parameters #
    ##############

    JobTitle : str  # REQUIRED
    InclCity : bool
    InclState : bool

    '''

    payload = dict(action="jobs-prog", v="1", format="json",
                   q="+".join(terms.split(" ")), useragent=x.head["user-agent"])
    payload.update(dict(**params))

    req = request_session.get(x.url, params=payload)



def Stats(terms, loc, **params):
    '''
    ##############
    # Parameters #
    ##############

    JobTitle : str  # REQUIRED
    InclCity : bool
    InclState : bool
    '''

    payload = dict(action="jobs-stats")
    payload.update(dict(**params))
    req = requests.get(x.url, params=payload)


def RefCodes(self, group):
    pass





        
        
         
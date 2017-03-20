from time import time
from configparser import ConfigParser
from urllib.parse import urlencode
from html import unescape

import os, re
import requests

import datetime
import requests_cache
import numpy as np
import json
from bs4 import BeautifulSoup as bsoup


from nltk import word_tokenize, sent_tokenize, pos_tag

ids = round(time()*100, 0)
wd = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))


class params:
    
    def __init__(self, city, state, fromage, terms, stopsfile):
        self.config = ConfigParser()
        self.config.read(wd('api.conf'))
        self.srcname, self.stopslist = None, None
        self.htmlkeys, self.args = None, None
        self.posturl = None
        self.useragent = hoodini.UserAgent().browser('Firefox', 0)
        self.pageurls = []

        self.city, self.state, self.fromage = city, state, fromage
        self.fmtterms, self.terms, self.stopsfile = None, terms, stopsfile
        self.stops = None

    def _format_searchterms(self, x):
        accepted_formats = [' ','-','_','|',':']
        if type(x) is list:
            terms = ' '.join(x)
            terms = '"'+terms+'"'
            return terms
        elif type(x) is str:
            for i in x:
                if i in accepted_formats:
                    terms = x.split(i)
                    terms = ' '.join(terms)
                else:
                    terms = x
                terms = '"'+terms+'"'
                return terms
        else:
            print("search term format not recognized. Accepted formats: strings joined by %s or list object\
Examples: 'computer+programmer' or ['computer','programmer']" % accepted_formats) 

    def _stops_list(self, file):
        if os.path.isfile(file):
            stops = np.loadtxt(file, dtype=np.str, converters={0:lambda x: x.decode('utf-8')})
        elif file == 'default':
            stops = np.loadtxt(wd('stops.ls'), dtype=np.str, converters={0:lambda x: x.decode('utf-8')})
        else:
            print("Stops file not found. Using defaults...")
            stops = np.loadtxt(wd('stops.ls'), dtype=np.str, converters={0:lambda x: x.decode('utf-8')})
        return stops

    def careerbuilder(self):

        ## API Docs: http://developer.careerbuilder.com/docs/v3jobid
        
        self.srcname = 'careerbuilder'
        self.conf = self.config['careerbuilder']
        self.stops = self._stops_list(self.stopsfile)
        

        self.htmlkeys = {0:('script', {'type':'application/ld+json'}),
                         18:'contactinfoemailurl',19:'contactinfophone',20:'contactinfoname',
                         21:'degreerequired',22:'experiencerequired',23:'travelrequired',
                         24:'managesothers',25:'degreerequiredcode',26:'categoriescodes',27:'employmenttypecode',
                         28:'industrycodes',29:'applyurl',30:'companydetailsurl'}

        self.args = {'DeveloperKey':self.conf['apikey'],
                     'outputjson':'false','ShowApplyRequirements':'True'}
        self.posturl, self.fmtterms = self.conf['url1'], self._format_searchterms(self.terms)

        
        
        for i in range(4):
            self.apiparams = {'DeveloperKey':self.conf['apikey'],'keywords':self.fmtterms,
                              'location':"%s, %s" % (self.city, self.state),'page_num':str(i),'sort':'desc',
                              'posted':'','emp':'ALL','pay':'0','company':'',"cat1":'',"cat2":'',
                              "cat3":'',"cb_apply":'false'}
            urlenc = urlencode(self.apiparams)
            u = ''.join([self.conf['url0'], urlenc])
            self.pageurls.append(u)
            

    def indeed(self):
        self.srcname = 'indeed'
        self.conf = self.config['indeed']
        self.stopslist = self._stops_list(self.stopsfile)

        self.htmlkeys = {0:('span', {'class':'company'}),
                         1:('span',{'class':'location'}),
                         2:('span',{'class':'date'}),
                         3:('b',{'class':'jobtitle'}),
                         4:('span',{'id':'job_summary','class':'summary'})}
        self.fmtterms = self._format_searchterms(self.terms)

        self.args = {'apikey':self.conf['apikey'],'srcname':self.srcname,
                     'city':self.city,'fromage':fromage,'state':state,
                     'terms':self.fmtterms}


        for i in range(3):
            s = i*25
            self.apiparams = {'publisher':self.conf['apikey'],'limit':'25','radius':'50','start':str(s),'fromage':self.fromage,
                              'l':"%s, %s" % (self.city, self.state),'q': self.fmtterms, 'useragent':self.useragent, 
                              'v':'2'}
            urlenc = urlencode(self.apiparams)
            u = ''.join([self.conf['url0'], urlenc])
            self.pageurls.append(u)
            
        
class query(object):

    
    def __init__(self, queryparams):

        self.src = queryparams
        self.stops = self.src.stopslist
        self.args = self.src.args
        self.srcname = self.src.srcname
        self.params = self.src.apiparams
        self.htmlkeys = self.src.htmlkeys
        self.pageurls = self.src.pageurls

        self.lists = togo.boxes().lists
        self.rows = togo.boxes().rows
        
        
        self.today = datetime.datetime.today()
        
    def response(self):
        requests_cache.install_cache(wd('apirequests'))
        
        f = lambda x, y: self.lists[x].append(str(y))
        clean = lambda x: unescape(x)
        strjoin = lambda x: ' '.join(x)
        findr = lambda x: ps.find(x)
        rmhtml = lambda x, y, z: x.replace(y, z) 
        
        if self.src.srcname is 'indeed':
            for page in self.pageurls:
                req0 = requests.get(page)
                searchsoup = bsoup(req0.text, 'html5lib')
                print(searchsoup.prettify())
                urlz = searchsoup.findAll('url')
                for u in range(0, len(urlz)):
                    url = urlz[u].string
                    req = requests.get(url)
                    soup = bsoup(req.text,'html5lib')
                    coname, location, jobage, title, summary = map(lambda x: soup.find(self.htmlkeys[x][0], self.htmlkeys[x][1]),
                                                                   [0, 1, 2, 3, 4])
                    title, coname = map(lambda x: re.sub('/','',x), [title.string, coname.string])
                    
                    rawtokens = word_tokenize(summary.get_text())
                    rawsents = sent_tokenize(summary.get_text())
                    rawtext = [s for s in rawsents]
                    rawtags = nltk.pos_tag(rawtokens)
                    tokens = []
                    
                    for s in rawtokens:
                        if s.lower() in self.stops: pass
                        elif len(s.lower()) <= 3: pass
                        else: tokens.append(s.lower())
                        
                    tags = nltk.pos_tag(tokens)
                    tokentags = []
                    for i in range(0, len(tags)):
                        tokentags.append(tags[0:][i][1])

                    pdd = jobage.string.split(' ', 2)[1]
                    dt = jobage.string.split(' ', 2)[0]             
                    if pdd == 'hours' and int(dt) <= int(12):
                        sdelt = datetime.timedelta(days=1)
                    elif pdd == 'hours' and int(dt) > int(12):
                        sdelt = datetime.timedelta(days=1)
                    elif pdd == 'days':
                        sdelt = datetime.timedelta(days=int(dt))
                    else:
                        print("No Date Found")

                    sdate = self.today - sdelt
                    edate = sdate + datetime.timedelta(9)
                    dr = self.today - edate
                    indict = {0:u,1:self.src.srcname,2:url[33:49],3:url,4:coname,5:title,6:location.string,7:jobage.string,
                              8:self.terms,9:summary.get_text(),10:strjoin(tokens) ,
                              11:strjoin(tokentags),12:location.string.split(", ", 1)[0],
                              13:location.string.split(", ", 1)[1],14:sdate.strftime('%m/%d/%Y'),
                              15:edate.strftime('%m/%d/%Y'),16:self.today.strftime("%m/%d/%Y %h:%m"),
                              17:edate-self.today}
                    
                       
                    [f(qq, indict[qq]) for qq in range(0, 18)]

              
        elif self.src.srcname is 'careerbuilder':
            for m in self.pageurls:
                req0 = requests.get(m)
                searchsoup = bsoup(req0.text, 'html5lib')
                urlsdf = json.loads(searchsoup.find(self.htmlkeys[0][0], self.htmlkeys[0][1]).string)

                for i in range(0, 25):
                    
                    try:
                        url = urlsdf['itemListElement'][i]['url']                        
                    except Exception as errmsg:
                        if errmsg is not None:
                            pass
                    else:
                        self.args.update({'DID':url[33:]})
                        paramenc = urlencode(self.args)
                        api1 = ''.join([self.src.posturl, paramenc])
                        req1 = requests.get(api1)
                        ps = bsoup(req1.text, 'lxml')
                        
                        if findr('enddate') is None: edate = self.today + datetime.timedelta(days=6)
                        else: edate = datetime.datetime.strptime(findr('enddate').string, '%m/%d/%Y')
                        if findr('begindate') is None: sdate = self.today - datetime.timedelta(days=3)
                        else: sdate = datetime.datetime.strptime(findr('begindate').string, '%m/%d/%Y')
                        if findr('jobdescription') is None: desctext = ' '
                        else: desctext = findr('jobdescription').get_text()
                        if findr('jobrequirements') is None: reqtext = ' '
                        else: reqtext = findr('jobrequirements').get_text()
                        if findr('locationcity') is None: cityy = self.city
                        else: cityy = findr('locationcity').string
                        if findr('locationstate') is None: states = self.state
                        else: states = findr('locationstate').string

                        days = edate - self.today
                        age = self.today - sdate

                        rawdesc, rawreq = clean(desctext), clean(reqtext)
                        rawtext = rawdesc+rawreq
                        htmltags = ['<b>','<div>','<strong>','<quot>','&nbsp',';','<u>',
                                    '<apos>','<it>',"<em>","<a>",'<span>','</quot>','</u>',
                                    'center',"<ul>",'<hr>',"</ul>","</hr>","</em>","</a>",
                                    '</span>','</li>','<br />','<br>','<li>','</strong>',
                                    '<p>','</p>','•','\r\n',"'",'|','"','</div>','</b>','/b']
                        for i in range(0, 32):
                            rawdesc = rmhtml(rawdesc, htmltags[i], ' ')
                            rawreq = rmhtml(rawreq, htmltags[i], ' ')
                            rawtext = rmhtml(rawtext, htmltags[i], ' ')
                            

                        sentdesc_raw, sentreq_raw, sentraw = sent_tokenize(rawtext), sent_tokenize(rawdesc), sent_tokenize(rawreq)
                        raw_desctokens, raw_reqtokens = word_tokenize(rawdesc), word_tokenize(rawreq)
                        rawtokens = word_tokenize(rawtext)

                          
                        tokens, tokentags, desctokens, reqtokens = [],[],[],[]
                        
                        for a in raw_desctokens:
                            if a in self.stops: pass
                            else: desctokens.append(a.lower())

                        for b in  raw_reqtokens:
                            if b in self.stops: pass
                            else: reqtokens.append(b.lower())

                        for c in rawtokens:
                            if c in self.stops: pass
                            else: tokens.append(c.lower())
                        
                        tags = pos_tag(tokens)
                        for i in range(0, len(tags)):
                            tokentags.append(tags[0:][i][1])


                        ## For persistent storage in SQL db tokens needed to be "chunked" as a single string
                        ## Just have to remember to add a str.split() after the db pull.  
                            
                        chunked_tokens, chunked_tags = strjoin(tokens), strjoin(tokentags)
                        chunked_desctokens, chunked_reqtokens = strjoin(desctokens), strjoin(reqtokens)

                        cbdict = {0:i,1:self.src.srcname, 2: url[33:], 3:url, 4:findr('company').string,
                                  5:findr('jobtitle').string, 6:"%s, %s" % (cityy, states),7:age, 8:self.src.terms,
                                  9: rawtext, 10:chunked_tokens, 11:chunked_tags,12:cityy,13:states,
                                  14:sdate.strftime("%m/%d/%Y"),15:edate.strftime("%m/%d/%Y"),
                                  16:self.today.strftime("%m/%d/%Y"),17:days}

                        [f(i, cbdict[i]) for i in range(0, 18)]  

                        for t in range(18, 31):
                            cbdict[t] = self.htmlkeys[t]
                            try:
                                d = findr(self.htmlkeys[t])
                            except Exception:
                                print("Not Found")
                                f(t, '')
                            else:
                                f(t, d.string)


api = params("san francisco", "ca", "7", ['business','analyst'], 'default')
api.careerbuilder()
q = query(api)
q.response()
print(q.lists)
    

                                


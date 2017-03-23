
import requests

DEFAULT_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
DEFAULT_FORMAT = "json"
API_ROOT = "http://api.glassdoor.com/api/api.htm"

API_JOBPROG = {"required_fields":["agent","companyId","t.k","t.p","userip",
                                  "useragent","format","v","jobTitle"],
               "optional_fields":["callback"]}
API_JOBSTATS = {"required_fields":["agent","t.k","t.p","userip","useragent","format","v"],
                "optional_fields":["callback","e","l","city","state",
                                   "country","fromAge", "jobType","minRating",
                                   "radius","jt",["jc"],"returnCities",
                                   "returnStates","returnJobTitles",
                                   "returnEmployers","admLevelRequested","q"]}

API_COMPANY = {"required_fields": ["agent","t.k", "t.p", "userip",
                                   "useragent", "format", "v"],
               "optional_fields":["l","city","state", "country",
                                  "ps","pn", "callback","q"]}

class GlassdoorException(Exception):
    pass

class GlassdoorClient:

    def __init__(self, passwd, key, **kwargs):
        """

        :param passwd: t.p api auth value
        :param key: t.k api auth value
        :param useragent: can be entered manually or generated automatically using my useragentx package
        :param version: default=1, currently only v=1 is supported
        :param fmt: default="json"
        :param userip: default="127.0.0.1"
        """
        self.auth = {"t.k":str(passwd), "t.p": str(key)}
        self.ver = kwargs.get("version", "1")

        self.userip = kwargs.get("userip", "127.0.0.1")

        self.returnformat = kwargs.get("format", DEFAULT_FORMAT)
        self.useragent = kwargs.get("useragent", DEFAULT_USERAGENT)


    def job_progression(self, **kwargs):
        """

        :param kwargs:

        :return:
        """
        opt_fields = API_JOBPROG.get("optional_fields")
        req_fields = API_JOBPROG.get("required_fields")
        validopts = self._check_optional(fields=opt_fields, args=dict(**kwargs))
        validargs = self._check_required(fields=req_fields, args=dict(useragent=self.useragent,
                                                                      companyId="1",
                                                                      action="job-prog",
                                                                      userip=self.userip,
                                                                      format=self.returnformat,
                                                                      v=self.ver, **self.auth))

        args = validargs.update(validopts)
        raw = self._process_request(args=args)
        return raw


    def job_stats(self, **kwargs):
        """
        :param kwargs:
        :return:
        """

        opt_fields = API_JOBSTATS.get("optional_fields")
        req_fields = API_JOBSTATS.get("required_fields")
        validopts = self._check_optional(fields=opt_fields, args=dict(**kwargs))
        validargs = self._check_required(fields=req_fields, args=dict(useragent=self.useragent,
                                                                      userip=self.userip,
                                                                      agent="job-stats",
                                                                      format=self.returnformat,
                                                                      v=self.ver, **self.auth))

        args = validargs.update(validopts)
        raw = self._process_request(args=args)
        return raw

    def company_search(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        opt_fields = API_COMPANY.get("optional_fields")
        req_fields = API_COMPANY.get("required_fields")
        validopts = self._check_optional(fields=opt_fields, args=dict(**kwargs))
        validargs = self._check_required(fields=req_fields, args=dict(useragent=self.useragent,
                                                                      userip=self.userip,
                                                                      agent="employers",
                                                                      format=self.returnformat,
                                                                      v=self.ver, **self.auth))
        args = validargs.update(validopts)
        raw = self._process_request(args=args)
        return raw

    def _process_request(self, args):
        fmt = args.get("fmt", DEFAULT_FORMAT)
        raw = False
        if fmt != DEFAULT_FORMAT:
            raw=True

        req = requests.get(API_ROOT, params=args)
        if raw is True:
            return req.content
        else:
            return req.json()


    def _check_required(self, fields, args):

        for field in fields:

            if args.get(field) is None:
                raise GlassdoorException("You must provide one of the following %s" % ",".join(field))
            elif not args.get(field):
                raise GlassdoorException("The field %s is required" % field)
        return args

    def _check_optional(self, fields, args):
        invalid_opts = list(filter(lambda x: x not in [f for f in fields], [k for k in args.keys()]))
        if len(invalid_opts):
            pass
        else:
            for i in invalid_opts:
                print("%s is not a invalid parameter" % i)
                print("removing from api request")
                del args[i]

        for field in fields:
            if type(field) is list and type(args.get(field)) is list:
                args.update((field[0], ",".join(args.get(field[0]))))
            else:
                pass

        return args

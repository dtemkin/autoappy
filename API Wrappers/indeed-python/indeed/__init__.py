import requests
import requests

ATTRIBUTION = '<span id="indeed_at"><a title="Job Search" href="https://www.indeed.com">jobs by <img alt=Indeed src="https://www.indeed.com/p/jobsearch.gif" style="border: 0; vertical-align: middle;"></a></span>'
DEFAULT_USERAGENT = ""
DEFAULT_USERIP = "127.0.0.1"
API_ROOT = "http://api.indeed.com/ads"
API_SEARCH = {"url": "%s/apisearch" % API_ROOT,
              'required_fields': ['userip', 'useragent', ['q', 'location']],
              "queryargs":["title","all_","any_","exact","none_"],
              "optional_fields":["get_pages", "company", "jobtype",
                                 "limit", "age", "radius", "salary",
                                 "app_platform", "directhire_only",
                                 "start", "show_latlong", "sort",
                                 "country", "chnl", "allow_duplicates",
                                 "callback", "highlight"]}


API_JOBS = {"url": "%s/apigetjobs" % API_ROOT,
            'required_fields': ["v", ['jobkeys']],
            "optional_fields":[]}
API_POST = {"url": "https://www.indeed.com/viewjob?", "required_fields":["ref"], "optional_fields":["htmlparser"]}



class IndeedException(Exception):
    pass


class IndeedClient:
    def __init__(self, apikey, version = "2", results_format="json"):
        """
        :param apikey:
            Insert PublisherID here.
            IsRequired: True
        :param version:
            Default: 2
            IsRequired: True
        :param results_format:
            Default: "json"
            IsRequired: True
        """
        self.auth = {"publisher":apikey}
        self.version = version
        self.results_format = results_format
        print(ATTRIBUTION)

    def _build_query(self, args):
        """
        :param args: dict
            Advanced search query arguments
            IsRequired: Yes
        :return: dict
            Returns dict of arguments with appropriate parameter assignments
        """
        queryarg_map = {
            "title": "as_ttl", "all": "as_and",
            "any": "as_any", "none": "as_not",
            "exact": "as_phr"
            }
        try:
            queryargs = dict(filter(lambda x: (queryarg_map[x], str(args[x])), [y for y in args.keys()]))
        except KeyError:
            raise IndeedException("Invalid key in args, must be one of the following: %s" % [k for k in queryarg_map.keys()])
        except TypeError:
            raise IndeedException("Query argument key is invalid type")
        else:
            return queryargs


    def _verify_optional_kwargs(self, optional_fields, args):


    def _verify_required_kwargs(self, required_fields, args):
        for field in required_fields:
            if type(field) is list:
                validation_list = [args.get(f) != None for f in field]
                if not (True in validation_list):
                    raise IndeedException("You must provide one of the following %s" % ",".join(field))
            elif not args.get(field):
                raise IndeedException("The field %s is required" % field)
        return args

    def advanced_search(self, queryargs, **optional_kwargs):
        """
        :param queryargs: dict
            Advanced search query arguments
            IsRequired: Yes
            :title: str or list
                Only return jobs that have these words in the title
                MapsTo: as_ttl
            :all_: str or list
                Only return jobs that have all of the keywords
                MapsTo: as_and
            :any_: str or list
                Only return jobs that have any of the keywords
                MapsTo: as_any
            :none_: str or list
                Only return jobs that have none of the keywords
                MapsTo: as_not
            :exact_: str or list
                Desc: Only return jobs that match these keywords exactly
                MapsTo: as_phr
        :param optional_kwargs:
            :get_pages:
                Desc: Try to get x number of pages of search results if available
                      If argument value exceeds number of pages will get all available
                Default: -1 (Value for "all" is -1, 0 is first page only)
                Notes: scaled on base 9 values with 0 indicating page 1
                IsRequired: No
            :company: str
                Desc: Only return jobs from company
                MapsTo: as_cmp
            :jobtype: str
                Desc: Return jobs that are of this particular type
                Default: "all"
                Accepted Values: ["fulltime","parttime","contract","internship"]
                MapsTo: jt
            :fmt: str
                Default: "json"
                Accepted Values: ["xml","json"]
                MapsTo: format
            :sort: str
                Desc: Change ordering method used to determine the order of the output
                Default: "date"
                Accepted Values: ["date" or "relevance"]
                MapsTo: sort
            :limit: int
                Desc: Limit the number of returned results
                Default: 50
                Accepted Values: [10, 20, 30, 50]
                MapsTo: limit
            :age: int
                Desc: The max age a returned post can be.
                Default: 15 (in days)
                MapsTo: fromage
            :location: str
                Desc: The location in which to focus the search
                Formats : ["Postal Code", "City, State/Province/Region"]
                MapsTo: l
            :radius: int
                Desc: The max radius in which to look for jobs
                Default: 50 (in miles)
                MapsTo: radius
            :salary: str or int
                Desc: Can be either minimum salary when information is provided or the acceptable range
                      See below for formatting guidelines
                Format: 40,000, 40K or as range: 40K-50K or 40000 - 50000
                MapsTo: salary
            :app_platform: str
                Desc: Where to retrieve posts from
                Default: "all"
                Accepted Values: ["jobsite", "employer", "all"]
                MapsTo: st
            :directhire_only: bool
                Desc: Show results from staffing agencies, direct hire or both
                Default: False
                MapsTo: sr
            :start: int
                Desc: Start Page
                Default: 0
                MapsTo: start
            :show_latlong: bool
                Desc: Return latitude and longitude for each result
                Default: True
                MapsTo: latlong
            :country: str
                Desc: Show results only from specified country
                Default: "us"
                MapsTo: co
            :chnl: str
                Desc: Grouping parameter for api requests. Most can ignore this.
                MapsTo: chnl
            :allow_duplicates: bool
                Desc: Filter duplicates and remove from results
                Default: True
                MapsTo: filter
            :callback: str
                Desc: The name of javascript function to which results should be returned. Only valid if format is 'json'.
                MapsTo: callback
            :version: int
                Default: 2
                Accepts: 1 or 2
                MapsTo: v
            :highlight: bool
                Desc: Show query string in bold
                Default: False
                MapsTo: highlight
        :return: str

        """
        baseurl = API_SEARCH["url"]
        if type(queryargs) is not dict:
            raise IndeedException("queryargs must be dict. for simple query run standard 'search' function")
        elif len([k for k in queryargs]) == 0:
            raise IndeedException("queryargs is required.")
        elif any([k for k in queryargs.keys()]) not in API_SEARCH["queryargs"]:
            raise IndeedException("Invalid query argument must be one of the following: %s" % API_SEARCH["queryargs"] )

        else:
            querydict = self._build_query(args=queryargs)

        req = requests.get()

    def search(self, query, **kwargs):
        """
        :param query: str, list
            IsRequired: Yes
            MapsTo: q
        :param optional_kwargs:
            :get_pages:
                Desc: Try to get x number of pages of search results if available
                      If argument value exceeds number of pages will get all available
                Default: -1 (Value for "all" is -1, 0 is first page only)
                Notes: scaled on base 9 values with 0 indicating page 1
                IsRequired: No
            :company: str
                Desc: Only return jobs from company
                MapsTo: as_cmp
            :jobtype: str
                Desc: Return jobs that are of this particular type
                Default: "all"
                Accepted Values: ["fulltime","parttime","contract","internship"]
                MapsTo: jt
            :fmt: str
                Default: "json"
                Accepted Values: ["xml","json"]
                MapsTo: format
            :sort: str
                Desc: Change ordering method used to determine the order of the output
                Default: "date"
                Accepted Values: ["date" or "relevance"]
                MapsTo: sort
            :limit: int
                Desc: Limit the number of returned results
                Default: 50
                Accepted Values: [10, 20, 30, 50]
                MapsTo: limit
            :age: int
                Desc: The max age a returned post can be.
                Default: 15 (in days)
                MapsTo: fromage
            :location: str
                Desc: The location in which to focus the search
                Formats : ["Postal Code", "City, State/Province/Region"]
                MapsTo: l
            :radius: int
                Desc: The max radius in which to look for jobs
                Default: 50 (in miles)
                MapsTo: radius
            :start: int
                Desc: Start Page
                Default: 0
                MapsTo: start
            :show_latlong: bool
                Desc: Return latitude and longitude for each result
                Default: True
                MapsTo: latlong
            :country: str
                Desc: Show results only from specified country
                Default: "us"
                MapsTo: co
            :chnl: str
                Desc: Grouping parameter for api requests. Most can ignore this.
                MapsTo: chnl
            :allow_duplicates: bool
                Desc: Filter duplicates and remove from results
                Default: True
                MapsTo: filter
            :callback: str
                Desc: The name of javascript function to which results should be returned. Only valid if format is 'json'.
                MapsTo: callback
            :version: int
                Default: 2
                Accepts: 1 or 2
                MapsTo: v
            :highlight: bool
                Desc: Show query string in bold
                Default: False
                MapsTo: highlight
        :return: str
        """
        baseurl = API_SEARCH["url"]



    def _arg_convert(self, args):

        return self._process_request(API_SEARCH.get('end_point'), self._valid_args(API_SEARCH.get('required_fields'), args))


    def jobs(self, jobkeys, **kwargs):
        """
        :param jobkeys:
            IsRequired: Yes
            Accepts
        :param kwargs:
        :kwargs version:
            Default: 2
            IsRequired: Yes
            Accepts: 1, 2
            MapsTo: v
        :return:
        """

        valid_args = self._valid_args(API_JOBS.get('required_fields'), args)
        valid_args['jobkeys'] = ",".join(valid_args['jobkeys'])
        return self._process_request(API_JOBS.get('end_point'), valid_args)

    def post(self, ref, htmlparser="html5lib"):
        """
        Uses the specified reference to retrieve the html of the post
        Then returns the scraped content from the beautifulsoup object

        :param ref: str or list
            Is the reference to use in the retrieval of the post
            Accepted Values: Can be url or jobkey (A jobkey is the key used for internal reference by indeed)
            Format: Can either be a single string or a list.
            IsRequired: True
        :param htmlparser:
            Desc: Parser to use with beautifulsoup
            Default: "html5lib"
            Accepts: Refer to beautifulsoup documentation
        :return: html
            Desc: Returns html object
        """

    def _next_page(self, page):


    def _process_request(self, endpoint, args):
        fmt = args.get("format", self.results_format)

        raw = True if format == 'xml' else args.get('raw', False)
        args.update({'v': self.version, 'format': format})

        r = requests.get(endpoint, params = args)
        return r.json() if not raw else r.content

    def _valid_args(self, required_fields, args):
        for field in required_fields:
            if type(field) is list:
                validation_list = [args.get(f) != None for f in field]
                if not (True in validation_list):
                    raise IndeedException("You must provide one of the following %s" % ",".join(field))
            elif not args.get(field):
                raise IndeedException("The field %s is required" % field)
        return args


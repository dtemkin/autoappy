
from API import careerbuilder, muse, indeed


class Data(object):

    def __init__(self):
        super(Data, self).__init__()
        self.data = {"Metadata":{}, "Posts":[], "SearchResults":[]}


class CodeReference(object):

    def __init__(self):
        super(CodeReference, self).__init__()
        self.ref = {"code":None, "text":None}

    @classmethod
    def Careerbuilder(cls, group):
        pass
    @classmethod
    def Indeed(cls, group):
        pass
    @classmethod
    def Muse(cls, group):
        pass
    @classmethod
    def Glassdoor(cls, group):
        pass

    def __dict__(self):
        return self.ref


class Search(Data):

    def __init__(self, terms, loc):
        super(Search, self).__init__()
        self.endpoint = "search"
        self.loc = loc


        if type(terms) is list:
            self.terms = "+".join(terms)
        else:
            self.terms = str(terms)



    def Careerbuilder(self, **kwargs):
        print("Searching Careerbuilder...")
        self.source = "careerbuilder"
        results = careerbuilder.Search(terms=self.terms, loc=self.loc, **kwargs)
        print("Careerbuilder: Found %s rows" % len(results))
        self.data["SearchResults"].extend(results)
        print("Careerbuilder: Search Done.")

    def Indeed(self, **kwargs):
        print("Searching Indeed...")
        self.source = "indeed"
        results = indeed.Search(terms=self.terms, loc=self.loc, **kwargs)
        print("Indeed: Found %s rows" % len(results))
        self.data["SearchResults"].extend(results)
        print("Indeed: Search Done.")

    def Muse(self, **kwargs):
        print("Searching Muse...")
        self.source = "muse"
        results = muse.Search(terms=self.terms, location=self.loc, **kwargs)
        print("Muse: Found %s rows" % len(results))
        self.data["SearchResults"].extend(results)
        print("Muse: Search Done.")

    def All(self):
        self.Muse()
        self.Careerbuilder()
        self.Indeed()


class Info(Data):

    def __init__(self, datadict, _id):
        super(Info, self).__init__()
        self.endpoint = "info"
        self.id = _id
        self.datadict = datadict

    def Careerbuilder(self):
        if self.datadict["source"] == "careerbuilder":
            self.source = "careerbuilder"
            print("Careerbuilder: Getting Post...")
            result = careerbuilder.Post(datadict=self.datadict, _id=self.id)
            print("Careerbuilder: Got Post %s @ %s" % (result[0]["jobtitle"], result[0]["company"]))
            self.data["Posts"].extend(result)
            print("Careerbuilder: Done.")
        else:
            pass

    def Indeed(self):
        if self.datadict["source"] == "indeed":
            print("Indeed: Getting Post...")
            self.source = "indeed"
            result = indeed.Post(datadict=self.datadict, _id=self.id)
            print("Indeed: Got Post %s @ %s" % (result[0]["jobtitle"], result[0]["company"]))
            self.data["Posts"].extend(result)
            print("Indeed: Done.")
        else:
            pass
    def Muse(self):
        if self.datadict["source"] == "muse":
            self.source = "muse"
            print("Muse: Getting Post...")
            result = muse.Post(datadict=self.datadict, _id=self.id)
            print("Muse: Got Post %s @ %s" % (result[0]["jobtitle"], result[0]["company"]))
            self.data["Posts"].extend(result)
            print("Muse: Done.")
        else:
            pass

    def All(self):
        self.Muse()
        self.Careerbuilder()
        self.Indeed()


class CompanyLookup(object):

    def __init__(self, *args, **kwargs):
        self.companydata = []

    def Muse(self):
        self.source = "muse"

    def Glassdoor(self):
        self.source = "glassdoor"

    def __iter__(self):
        return self.companydata

class CompanyList(object):

    def __init__(self, **filters):
        self.source = "muse"
        self.companies = []

    def __iter__(self):
        return self.companies


class Other(object):

    def __init__(self):
        self.source = None

    def Stats(self):
        self.source = "glassdoor"
        baseurl = ""

    def Progression(self):
        self.source = "glassdoor"


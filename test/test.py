'''
Created on Dec 12, 2016

@author: dysmas
'''

from mcjobs.API.Job import Search, Info
from mcjobs.utils import fullpath

from pprint import PrettyPrinter



posts = []
pp = PrettyPrinter(indent=2, width=4)
search = Search(terms=["Data", "Analyst"], loc="Chicago")
search.Muse()
for i in range(len(search.data["SearchResults"])):
    info = Info(datadict=search.data["SearchResults"][i], _id=i)
    info.Muse()

    posts.extend(info.data["Posts"])

pp.pprint(posts)


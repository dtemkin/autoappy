'''
Created on Dec 12, 2016

@author: dysmas
'''

from pprint import PrettyPrinter

from API.Job import Search, Info



posts = []
pp = PrettyPrinter(indent=2, width=4)
search = Search(terms=["Data", "Analyst"], loc="Chicago")
search.Muse()
for i in range(len(search.data["SearchResults"])):
    info = Info(datadict=search.data["SearchResults"][i], _id=i)
    info.Muse()

    posts.extend(info.data["Posts"])

pp.pprint(posts)


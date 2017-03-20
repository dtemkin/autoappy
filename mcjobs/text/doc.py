'''
@author: Dan Temkin
@email: 


'''
from abc import ABCMeta
import sqlite3
from collections import OrderedDict, namedtuple
from mcjobs.text.base import Text, Document


class Application(Document):
    def __init__(self):
        super(Application, self).__init__()
        self.url = None

        self.contactinfo = {}
        self.status = None
        self.docs = []
        self.fields = {}.fromkeys(["name","type","default","is_form"], None)
        self._id = None

    @classmethod
    def check_status(self, db=fullpath("../../applications.db")):
        stmt = '''SELECT * FROM main WHERE srcid = ? '''
        conn = sqlite3.connect(database=db, isolation_level="DEFERRED")
        curs = conn.cursor()
        curs.execute(stmt, (self._id, ))
        rows = [row for row in curs]
        if len(rows) > 1:
            print("Found multiple rows!")
            print([",".join([row["company"], row["title"], row["status"]+"\n"]) for row in rows])
        elif len(rows) == 1:
            print("Found row.\n")
            print(rows[0])
            return True, rows[0]["status"]
        elif len(rows) == 0:
            print("Invalid Reference ID, No Row Found.")

    @property
    def docfields(self):
        return self.fields

class Resume(Application, Text):
    pass

class CoverLetter(Application, Text):
    pass

from sqlite3 import dbapi2 as sqlite3
from database import Database


class binaryTags:
    def __init__(self):
        self.tags={}

    def __init__(self, dict):
        self.tags = dict
        
    def __init__(self, query, primaryKey):
        for row in query:
            t = row[primaryKey]
            self.tags[t] = 1
    def __init__(query, args=(), primaryKey):
        res = Database.query(query, args)
        __init__(res, primaryKey)

    def getTags():
        return self.tags

    def get(tag):
        try:
            return self.tags[tag]
        except KeyError as e:
            return 0


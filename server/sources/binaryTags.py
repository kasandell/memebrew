from sqlite3 import dbapi2 as sqlite3
from database import Database


class binaryTags(object):
    '''
    def __init__(self):
        self.tags={}

    def __init__(self, dict):
        self.tags = dict


    def __init__(self, arr):
        for item in arr:
            self.tags[ item ] = 1

        
    def __init__(self, query, primaryKey):
    '''

    def __init__(self, primaryKey, query, args=()):
        print query, args
        print 'what'
        self.tags = {}
        res = Database.query(query, args)
        for row in res:
            t = row[primaryKey]
            self.tags[t] = 1

    def getTags(self):
        return self.tags

    def get(self, tag):
        try:
            return self.tags[tag]
        except KeyError as e:
            return 0


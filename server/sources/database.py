from flask import Flask, app_ctx_stack, send_file
from sqlite3 import dbapi2 as sqlite3



class Database:
    DATABASE = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/database/meme.db'
    '''
    #initialize with default name
    def init():
        this.DATABASE = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/database/meme.db'
    #initialize with a databse name
    def init(dbName):
        this.DATABASE = dbName
    '''
    #get the current databse
    @staticmethod
    def getDB():
        top = _app_ctx_stack.top
        if not hasattr(top, 'sqlite_db'):
            top.sqlite_db = sqlite3.connect(this.DATABASE)
            top.sqlite_db.row_factory = sqlite3.Row
        return top.sqlite_db
    #execute a query that returns something from the database
    @staticmethod
    def query(query, args=(), one=False):
        cur = getDB.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    #execute a query that changes the database
    @staticmethod
    def execute(query, args=()):
        db = getDB()
        db.execute(query, args)
        db.commit()

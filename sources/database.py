from flask import Flask, _app_ctx_stack, send_file
from sqlite3 import dbapi2 as sqlite3
from config import config



class Database(object):
    DATABASE = config.get('databaseLocation')#'/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/database/meme.db'
    #get the current databse
    @staticmethod
    def getDB():
        top = _app_ctx_stack.top
        if not hasattr(top, 'sqlite_db'):
            top.sqlite_db = sqlite3.connect(Database.DATABASE)
            top.sqlite_db.row_factory = sqlite3.Row
        return top.sqlite_db
    #execute a query that returns something from the database
    @staticmethod
    def query(query, args=(), one=False):
        cur = Database.getDB().execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    #execute a query that changes the database
    @staticmethod
    def execute(query, args=()):
        db = Database.getDB()
        db.execute(query, args)
        db.commit()

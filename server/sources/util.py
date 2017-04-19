from database import Database
#from image import image
import image
from binaryTags import binaryTags
from flask import session, jsonify
from config import config
baseImageDir = 'http://127.0.0.1:5000/img'


class utils(object):
    UPLOADS_FOLDER = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/storage/'
    ALLOWED_EXTENSIONS = ['gif', 'png', 'jpeg', 'jpg']
    @staticmethod
    def returnMessage(success, reason=None):
        if reason is None:
            return jsonify({
                'success': success
                })
        else:
            return jsonify({
                'success': success,
                'reason': reason
                })
    @staticmethod 
    def queryLength(query):
        count = 0
        for row in query:
            count += 1
        return count

    @staticmethod
    def square(val):
        return val*val



    @staticmethod
    def deleteFromTable(image, table, userID):
        qString = 'delete from ' + table + ' where userid=? and image=?'
        Database.execute(qString, [ userID, image.permID ])

    @staticmethod
    def insertIntoTable(image, table, userID):
        qString = 'insert into ' + table + '(userid, image) select ?,?'
        Database.execute(qString, [ userID, image.permID] )

    @staticmethod
    def validateTableName(tableName):
        return True if (tableName == config.get('likeTable') or tableName == config.get('dislikeTable') ) else False

    @staticmethod
    def checkQueryExistence(query, args=()):
        res = Database.query(query, args)
        ret = True if (res is not None) else False
        return True if res is not None else False

    @staticmethod
    def checkIfImagePresent(image, tableName):
        qString = 'select * from ' + tableName + ' where userid=? and image=?'
        return utils.checkQueryExistence(qString, [ str(session['userid']), str(image.permID) ])


    @staticmethod
    def dislikeTag(tag, userID):
        if utils.checkQueryExistence('select 1 from tagdislikes where userid=? and idnumber=?', [ userID, tag]):
            Database.execute('update tagdislikes set count=count+1 where userid=? and idnumber=?' [ userID, tag ])
            Database.execute('update taglikes set count=count-1 where userid=? and idnumber=?' [ userID, tag ])
        else:
            Database.execute('insert into tagdislikes(userid, idnumber, count) select ?,?,?', [ userID, tag, 1])

        
    @staticmethod
    def likeTag(tag, userID):
        if utils.checkQueryExistence('select 1 from taglikes where userid=? and idnumber=?', [ userID, tag]):
            Database.execute('update taglikes set count=count+1 where userid=? and idnumber=?' [ userID, tag ])
            Database.execute('update tagdislikes set count=count-1 where userid=? and idnumber=?' [ userID, tag ])
        else:
            Database.execute('insert into taglikes(userid, idnumber, count) select ?,?,?', [ userID, tag, 1])



    @staticmethod
    def extractTags(tagStr):
        tgArr = tagStr.split(',')
        tgArr = [f.strip() for f in tgArr]
        tgArr = [str(f).lower() for f in tgArr if (f is not '' and f is not None)]
        return tgArr

    @staticmethod
    def createLink(permID):
       return config.get('baseImageDir') + '/' + permID 
    
    @staticmethod
    def getImageType(imgName):
        if imgName[-4:].lower() == '.jpg' or imgName[-4:].lower() == '.png' or imgName[-4:].lower() == '.gif':
            return imgName[-4:].lower()
        if imgName[-5:].lower() == '.jpeg':
            return imgName[-5:].lower()

    @staticmethod
    def allowedFile(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in utils.ALLOWED_EXTENSIONS

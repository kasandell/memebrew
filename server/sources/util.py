from database import Database
#from image import image
import image
from binaryTags import binaryTags
from flask import session
from config import config
dislikesTable = 'dislikes'
likesTable = 'likes'
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
        Database.execute('delete from ? where userid=? and image=?', [ table, userID, image ])

    @staticmethod
    def insertIntoTable(image, table, userID):
        Database.execute('insert into ?(userid, image) select ?,?' [ table, userID, image] )

    @staticmethod
    def validateTableName(tableName):
        return True if tableName is likesTable or tableName is dislikesTable else False

    @staticmethod
    def checkQueryExistence(query, args=()):
        res = Database.execute(query, args)
        return True if res is not None else False

    @staticmethod
    def checkIfImagePresent(image, tableName):
        return checkQueryExistence('select 1 from ? where userid=? and iamge=?', [ tableName, session['userid'], image.permID ])


    @staticmethod
    def dislikeTag(tag, userID):
        if checkQueryExistence('select 1 from tagdislikes where userid=? and idnumber=?', [ userID, tag]):
            Database.execute('update tagdislikes set count=count+1 where userid=? and idnumber=?' [ userID, tag ])
            Database.execute('update taglikes set count=count-1 where userid=? and idnumber=?' [ userID, tag ])
        else:
            Database.execute('insert into tagdislikes(userid, idnumber, count) select ?,?,?', [ userID, tag, 1])

        
    @staticmethod
    def likeTag(tag, userID):
        if checkQueryExistence('select 1 from taglikes where userid=? and idnumber=?', [ userID, tag]):
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
       print config.get('baseImageDir')
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

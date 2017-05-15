from sqlite3 import dbapi2 as sqlite3
from scoreImage import scoreImage
from binaryTags import binaryTags
from database import Database
from config import config
from util import utils
import uuid
import os
from flask import send_file, request, session

class image(object):
    def __init__(self, arg):
        try:
            print 'made it'
            test = arg.form['tags'] #will fail here
            print 'no'
            self.createImage(arg)
        except AttributeError as e:
            self.weights = {}
            self.tags = None
            self.caption = None
            self.imageURL = None
            self.totalLikes = None
            self.totalDislikes = None
            self.score = None
            self.permID = str(arg)
            self.image = self.permID;
            self.updateTotalLikes()
            self.updateTotalDislikes()
            self.updateScore()
            self.loadTags()
            self.loadImageWeights()
            self.getInfo()
            self.image_url = self.imageURL

    def getInfo(self):
        q = Database.query('select caption, image_url from uploads where image=?', [ self.permID ], one=True)
        try:
            self.imageURL = str(q['image_url'])
            self.caption = str(q['caption'])
        except Exception as e:
            self.imageURL = None
            self.caption = None
        #we use this init only when first time image is created, so we upload it to database
    def createImage(self, request):

        fl = request.files['file']
       
        self.permID = str(uuid.uuid1())
        self.tags = utils.extractTags(request.form['tags'])
        self.caption = request.form['caption']
        self.fname = (self.permID + utils.getImageType(fl.filename) )
        self.link = utils.createLink(self.fname)
        self.__addToDatabase()
        fl.save(os.path.join( config.get('uploadsFolder'), self.fname ) )
        

    def __addToDatabase(self):
        Database.execute('insert into uploads(image, image_url, caption, userid) select ?,?,?,?', [self.permID, self.link, self.caption, session[ 'userid' ] ])
        for tag in self.tags:
            Database.execute('insert into tagmaps(tagname) select ? where not exists(select 1 from tagmaps where tagname=?)', [tag, tag])
            val = Database.query('select idnumber from tagmaps where tagname=?', [tag], one=True)['idnumber']
            Database.execute('insert into imageTags(image, idnumber) select ?,?', [self.permID, int(val)])
        
        self.setScore()



    def loadImageAttributes(self):
        infoQuery = Database.query('select caption, image, image_url from Uploads where image=?', [ self.permID ])
        if infoQuery is not None:
            self.caption = str( infoQuery[ 'caption' ])
            self.imageURL = str( infoQuery[ 'image_url' ])

    
    def loadImageWeights(self):
        weightQuery = Database.query('select idnumber from imagetags where image=?', [ self.permID ])
        for w in weightQuery:
            print w
            self.weights[ w['idnumber'] ] = 1
            

    def getTotalLikes(self):
        likes = Database.query('select * from likes where image=?', [ self.permID ])
        return utils.queryLength(likes)

    #update locally to respond to server changes
    def updateTotalLikes(self):
        self.totalLikes = self.getTotalLikes()

    def getLocalLikes(self):
        return self.totalLikes


    def getTotalDislikes(self):
        dislikes = Database.query('select * from likes where image=?', [ self.permID ])
        return utils.queryLength(dislikes)

    def updateTotalDislikes(self):
        self.totalDislikes = self.getTotalDislikes()
    
    def getLocalDislikes(self):
        return self.totalDislikes

    def getScore(self):
        sc = Database.query('select * from imagescores where image=?', [ self.permID ], one=True)
        print 'score: ', sc
        return sc if sc is not None else None

    def updateScore(self):
        self.score = self.getScore()
        print 'self score: ', self.score

    def setScore(self):
        val = scoreImage.score(self.permID)
        print 'score: ', val
        if self.getScore() is not None:
            Database.execute('update imagescores set score=? where image=?', [ val, self.permID ])
        else:
            Database.execute('insert into imagescores(image, score) select ?, ?', [ self.permID, val ])

        return val
    
    def loadTags(self):
        self.tags = binaryTags('idnumber', 'select idnumber from imagetags where image=?', [ self.permID ])

    def getTags(self):
        return self.tags.getTags()

    def getTag(self, tag):
        return self.tags.get(tag)


    def getTagWeights(self):
        return self.getTags()

    def getTagWeight(self, tag):
        return self.getTag( tag)

    def getWeightForTag(self, tag):
        return self.getTag(tag)

    def jsonify(self):
        return {'caption':self.caption, 'image':self.permID, 'image_url':self.imageURL}


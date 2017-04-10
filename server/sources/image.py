from sqlite3 import dbapi2 as sqlite3
from scoreImage import scoreImage
from binaryTags import binaryTags
from database import Database
from util import utils

class Image:
    def __init__(permID):
        self.permID = str(permID)
        updateTotalLikes()
        updateTotalDislikes()
        updateScore()
        loadTags()
        loadImageWeights()
    
    def loadImageWeights():
        weightQuery = Database.query('select idnumber from imagetags where image=?', [ self.permID ])
        for w in weightQuery:
            self.weights[ w['idnumber'] ] = 1
            

    def getTotalLikes():
        likes = Database.query('select * from likes where image=?', [ self.permID ])
        return queryLength(likes)

    #update locally to respond to server changes
    def updateTotalLikes():
        self.totalLikes = getTotalLikes()

    def getLocalLikes():
        return self.totalLikes


    def getTotalDislikes():
        dislikes = Database.query('select * from likes where image=?' [ self.permID ])
        return queryLength(dislikes)

    def updateTotalDislikes():
        self.totalDislikes = getTotalDislikes()
    
    def getLocalDislikes():
        reutrn self.totalDislikes

    def getScore():
        sc = Database.query('select 1 from imagescores where image=?', [ self.permID ])
        return sc if sc is not None else None

    def updateScore():
        self.score = getScore()
    def setScore():
        val = score(self.permID)
        if getScore() is not None:
            Database.execute('update imagescores set score=? where image=?', [ val, self.permID ])
        else:
            Databse.execute('insert into imagescore(image, score) select ?, ?', [ self.permID, val ])
        return val
    
    def loadTags():
        self.tags = binaryTags('select idnumber from imagetags where image=?', [ self.permID ], 'idnumber')

    def getTags():
        return self.tags.getTags()

    def getTag(tag):
        return self.tags.get(tag)


    def getTagWeights():
        return def getTags()

    def getTagWeight(tag):
        return getTag(tag)

    def getWeightForTag(tag):
        return getTag(tag)

    #make self private
    #just gets us the number of elements in the query

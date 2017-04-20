from flask import session
from util import utils
from database import Database
from userWeights import userWeights
from config import config



class user(object):
    def __init__(self, userID):
        self.userID = userID
        self.userWeights = userWeights(self.userID)

    def updateLikesAndDislikes(self, image, primaryTable):
        print 'hello'
        if session['userid'] != self.userID:
            print 'no user'
            return utils.returnMessage(False, 'User liking image must be the user who is logged in')
        if not utils.validateTableName(primaryTable):
            print 'tbl nt found'
            return utils.returnMessage(False, 'Unable to find requested table')
        secondaryTable = config.get('likeTable') if primaryTable is config.get('dislikeTable') else config.get('dislikeTable')
        if utils.checkIfImagePresent(image, primaryTable):
            print 'already liked'
            return utils.returnMessage(False, 'Cannot execute duplicate action on image')#can't like/dislike twice
        seenImageBefore = utils.checkIfImagePresent(image, secondaryTable)#we'll need self for tags later
        print 'deleting from', secondaryTable
        utils.deleteFromTable(image, secondaryTable, self.userID)
        print 'inserting into', primaryTable
        utils.insertIntoTable(image, primaryTable, self.userID)
        print 'should be in'
        #given new likes/dislikes rescore the image
        v = image.setScore()
        for tag in image.getTags():
            if primaryTable == config.get('likeTable'):
                utils.likeTag(tag, self.userID)
            else:
                utils.dislikeTag(tag, self.userID)
        return utils.returnMessage(True)

    def likeImage(self, image):
        return self.updateLikesAndDislikes(image, config.get('likeTable') )

    def dislikeImage(self, image):
        return self.updateLikesAndDislikes(image, config.get('dislikeTable') )
    
    def setWeights(self, weights):
        self.userWeights = weights
    
    def getWeights(self):
        return self.userWeights.getTagWeights()

    def getWeightForTag(self, tag):
        return self.userWeights.getWeightForTag(tag)

    def getTagWeights(self):
        return self.getWeights()

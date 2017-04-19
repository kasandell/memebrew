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
        if session['userid'] != self.userID:
            return utils.returnMessage(False, 'User liking image must be the user who is logged in')
        if not utils.validateTableName(primaryTable):
            return utils.returnMessage(False, 'Unable to find requested table')
        secondaryTable = config.get('likeTable') if primaryTable is config.get('dislikeTable') else config.get('dislikeTable')
        if utils.checkIfImagePresent(image, primaryTable):
            return utils.returnMessage(False, 'Cannot execute duplicate action on image')#can't like/dislike twice
        seenImageBefore = utils.checkIfImagePresent(image, secondaryTable)#we'll need self for tags later
        utils.deleteFromTable(image, secondaryTable, self.userID)
        utils.insertIntoTable(image, primaryTable, self.userID)
        #given new likes/dislikes rescore the image
        image.setScore()
        for tag in image.getTags():
            if primaryTable == config.get('likeTable'):
                utils.likeTag(self.userID, tag)
            else:
                dislikeTag(self.userID, tag)
        return utils.returnMessage(True)

    def likeImage(self, image):
        return self.updateLikesAndDislikes(image, config.get('likeTable') )

    def dislikeImage(self, image):
        return self.updateLikesAndDislikes(image, config.get('dislikeTable') )
    
    def setWeights(self, weights):
        self.userWeights = weights
    
    def getWeights(self):
        return self.userWeighst.getWeights()

    def getWeightForTag(self, tag):
        return self.userWeights.getWeightForTag(tag)

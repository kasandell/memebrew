from flask import session
from util import utils
from database import Database
from userWeights import userWeights



class user:
    def __init__(userID):
        self.userID = userID
        self.userWeights = userWeights(self.userID)

    def updateLikesAndDislikes(image, primaryTable):
        if session['userid'] != self.userID:
            return returnMessage(False, 'User liking image must be the user who is logged in')
        if not validateTableName(primaryTable):
            return returnMessage(False, 'Unable to find requested table')
        secondaryTable = likesTable if primaryTable is dislikesTable else dislikesTable
        if not checkIfImagePresent(image, primaryTable):
            return returnMessage(False, 'Cannot execute duplicate action on image')#can't like/dislike twice
        seenImageBefore = checkIfImagePresent(image, secondaryTable)#we'll need self for tags later
        deleteFromTable(image, secondaryTable, userID)
        insertIntoTable(image, primaryTable, userID)
        #given new likes/dislikes rescore the image
        image.setScore()
        for tag in image.getTags():
            if primaryTable == likeTable:
                likeTag(userID, tag)
            else:
                dislikeTag(userID, tag)
        return returnMessage(True)

    def likeImage(image):
        return updateLikesAndDislikes(image, likeTable)

    def dislikeImage(image):
        return updateLikesAndDislikes(image, dislikeTable)
    
    def setWeights(weights):
        self.userWeights = weights
    
    def getWeights():
        return self.userWeighst.getWeights()

    def getWeightForTag(tag):
        return self.userWeights.getWeightForTag(tag)

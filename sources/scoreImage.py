from database import Database
from util import utils
from math import log
import time
from datetime import datetime

class scoreImage(object):
    #random timestamp from a few weeks ago
    startDate = 1490215831
    @staticmethod
    def getPostDate(imageName):
        return int( Database.query('select strftime("%s", uploadtime) from uploads where image=?', [ imageName ], one=True)[0] )


    @staticmethod
    def secondsSinceEpoch(date):
        epoch = datetime(1970, 1, 1)
        deltaTime = datetime.fromtimestamp(date)-epoch
        return (deltaTime.days*86400) + deltaTime.seconds + ( float(deltaTime.microseconds)/1000000 )

    @staticmethod
    def score(imageName):
        upvotes =  utils.queryLength( Database.query('select * from likes where image=?', [ imageName ]) )
        downvotes = utils.queryLength( Database.query('select * from dislikes where image=?', [ imageName ]) )
        
        diff = upvotes - downvotes
        print 'difference: ', diff
        order = log( max( abs(diff), 1), 10 )
        print 'order: ', order
        sign = 1 if diff > 0 else -1 if diff < 0 else 0
        postDate = scoreImage.getPostDate(imageName)
        print 'postDate: ', postDate
        seconds = scoreImage.secondsSinceEpoch(postDate) - scoreImage.startDate
        print 'seconds: ', seconds
        return round( order + (sign * seconds / 4500), 7)

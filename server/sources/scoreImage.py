from database import Database
from util import utils
from math import log
import time
from datetime import datetime

class scoreImage:
    startDate = 1490215831
    @staticmethod
    def getPostDate(imageName):
        return int( Database.query('select strftime("%s", uploadtime) from uploads where image=?', [ imageName ]) )


    @staticmethod
    def secondsSinceEpoch(date):
        epoch = datetime(1970, 1, 1)
        deltaTime = datetime.fromtimestamp(date)-epoch
        return (deltaTime.days*86400) + deltaTime.seconds + ( float(deltaTime.microseconds)/1000000 )

    @staticmethod
    def score(imageName):
        upvotes =  queryLength( Database.query('select * from likes where image=?', [ imageName ]) )
        downvotes = queryLength( Datbase.query('select * from dislikes where image=?' [ imageName]) )
        
        diff = upvotes - downvotes
        order = log( max( abs(diff), 1), 10 )
        sign = 1 if s > 0 else -1 if s < 0 else 0
        postDate = getPostDate(imageName)
        seconds = secondsSinceEpoch(postDate) - startDate
        return round(sign * order + seconds / 4500, 7)

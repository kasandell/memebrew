from database import Database


class userWeights(object):
    def __init__(self, userID):
        self.tagWeights = self.calculateTagWeights( str(userID) )
        print 'tagWeights:', self.tagWeights

    def calculateTagWeights(self, userID):
        likes = Database.query('select idnumber, count from taglikes where userid=?', [ userID ])
        dislikes = Database.query('select idnumber, count from tagdislikes where userid=?', [ userID ])
        tw = {}
        tags = set()
        for l in likes:
            tags.add(l['idnumber'])

        for d in dislikes:
            tags.add(d['idnumber'])
        
        #TODO: we can make a much more sophisticated weighting algorithm
        for tag in tags:
            totalSeen = 0
            count = 0
            for l in likes:
                if l['idnumber'] == tags:
                    totalSeen = totalSeen + int( l['count'] ) 
                    count = count + int( l['count'] )

            for d in dislikes:
                if d['idnumber'] == tag:
                    totalSeen = totalSeen + int( d['count'] )
                    count = count - int (d['count'] )
            
            tw[ tag ] = (0 if totalSeen == 0 else float( count/totalSeen ))
            return tw

    def getWeightForTag(self, tag):
        try:
            return self.tagWeights[tag]
        except KeyError as e:
            return 0

    def getTagWeights(self):
        return self.tagWeights

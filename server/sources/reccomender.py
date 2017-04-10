from database import Database
from user import user
from operator import itemgetter


class recommender:
    def __init__(self, userID):
        self.userID = userID
        self.user = user(userID)
        self.lastXImages = 30
        self.lastXUsers = 40
        self.topXUsers = 20

    def __getPastImages(self):
       pastImages = Database.query('select image from lkes where userid=? limit ?', [ self.userID, self.lastXImages ])
        return [f['image'] for f in pastImage]  

    def __getLikersFromImages(self, images):
        uSet = set()
        for image in images:
            uNames = Database.query('select userid from likes where (image=? and NOT userid=?) limit ?', [ image, self.userID, self.lastXUsers ])
            #unique users only
            [uSet.add( str(f['userid']) ) for f in uNames]
        uNameList = [f for f in uSet] 
        return [user(f) for f in uNameList] # returns us a list of users

    def __getMostPromisingUsers(self, users):
        dists = []
        for u in users:
            dists.append(u, distance(u))
         dists = sorted(dists, key = itemgetter(1))
         dists = [f[0] for f in dists]
         return (dists[:self.topXUsers] if len(dists) < self.topXUsers else dists)

    
    #calculate euclidian distance between two tag sets, but don't square root because it is computationally expensive
    def __distance(self, u):
        count = 0
        tagsSeen = set()
        for tag in self.user.getTagWeights():
            count += float( square( self.user.getWeightForTag(tag) - u.getWeightForTag(tag) ) )
            tagsSeen.add(tag)

        for tag in u.getTagWeights():
            if tag not in tagsSeen:
                count += float( square( self.user.getWeightForTag(tag) - u.getWeightForTag(tag) ) )
         return count

     def __getImagesFromUsers(self, userList):
            unlikedImages = set()
            userLikes = Database.query('select image from likes where userid=?', [ self.userID ])
            userSet = set()
            [userSet.add(f['image']) for f in userLikes]
            for user in promising:
                otherLikesQuery = Database.query('select imagr from likes where userid=?', [ user ])
                otherLikes = [f['image'] for f in otherLikesQuery]
                difLikes = [x for x in otherLikes if x not in userSet]
                [unlikedImages.add(f) for f in difLikes]

            unlikedImages = [image(f) for f in unlikedImages]
            imageWeights = [(f, calcWeighDifference(f) ) for f in unlikedImages]
            imageWeights = sorted(imageWeights, key=itemgetter(1))
            return [ f[0] for f in imageWeights ]
            



        def __calcWeightDifference(image):
            return distance(image) 


             

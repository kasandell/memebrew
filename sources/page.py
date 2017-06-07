from flask import request, session, g, jsonify
from config import config
from database import Database
from recommender import recommender
from image import image
import random


class page(object):
    def __init__(self, request):
        self.request = request

    def __getPage(self):
        if session['page_title'] == 'hot':
            return self.generateHot()
        elif session['page_title'] == 'fresh':
            return self.generateFresh()
        else:
            return None

    def getPage(self):
        return self.__getPage()
    
    def getJSON(self):
        msg = self.__getPage()
        print [{'image_url':f.imageURL, 'caption':f.caption, 'score': f.score, 'image':f.permID} for f in msg]
        return jsonify([{'image_url':f.imageURL, 'caption':f.caption, 'score': f.score, 'image':f.permID} for f in msg])

    def generateHot(self):
        after = self.request.args.get('after')
        if after is None:
            print 'no after'
            msg = None
            if g.user:
                print 'we have a user'
                msg = Database.query('''select image from Uploads ul 
                        where (select score from imagescores where image=ul.image) > ? 
                        and ul.image not in (select image from likes where userid=?)
                        order by (select score from imagescores where image=ul.image) desc 
                        limit ?''', 
                        [ config.get('hotFloor'), session['userid'], config.get('perPage') ] )
                print [f['image'] for f in msg], 'IMAGES'
            else:
                print 'no user'
                msg = Database.query('''select image from Uploads ul 
                        where (select score from imagescores where image=ul.image) > ? 
                        order by (select score from imagescores where image=ul.image) desc 
                        limit ?''', 
                        [ config.get('hotFloor'), config.get('perPage') ] )

            hot = [ image(f['image']) for f in msg ]
            print 'hot: ', hot
            recs = []
            if g.user:
                rc = recommender( session['userid'] )
                recs = rc.getRecommendations()
                print 'recs ', recs
               
            ret = self.__createFeed(hot, recs)
            print 'final: ', ret

            return ret

        print "we found an after parameter, and it is", after
                
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        msg = None
        if g.user:
            msg = Database.query('''select image from uploads ul 
                        where (select score from imagescores where image=ul.image) < ? 
                        and (select score from imagescores where image=ul.image) > ? and
                        ul.image not in (select image from likes where userid=?)
                        order by (select score from imagescores where image=ul.image) desc 
                        limit ?''', 
                        [ score, config.get('hotFloor'), session['userid'], config.get('perPage')] )
        else:
            msg = Database.query('''select image from uploads ul 
                        where (select score from imagescores where image=ul.image) < ? 
                        and (select score from imagescores where image=ul.image) > ? 
                        order by (select score from imagescores where image=ul.image) desc 
                        limit ?''', 
                        [ score, config.get('hotFloor'), config.get('perPage')] )

        hot = [ image(f['image']) for f in msg ]
        print 'hot: ', hot
        recs = []
        if g.user:
            rc = recommender( session['userid'] )
            recs = rc.getRecommendations()
            print 'recs ', recs

        ret = self.__createFeed(hot, recs)
        print 'final: ', ret
        return ret

  
    def __createFeed(self, hot, recs):
        if hot == []:
            l = [f for f in recs]
            random.shuffle(l)
            random.shuffle(l)
            return [image(f) for f in l]
        a = set()
        lHot = hot[-1]
        hot = hot[:-1]
        [a.add(f.permID) for f in hot]
        [a.add(f.permID) for f in recs]
        l = [f for f in a]
        random.shuffle(l)
        random.shuffle(l)
        l = [image(f) for f in l]
        l.append(lHot)
        return l
        

    #TODO: for fresh, consider ordering based solely on upload date
    def generateFresh(self):
        after = self.request.args.get('after')
        if after is None:
            msg = None
            if g.user:
                msg = Database.query('''select image from uploads ul
                            where (select score from imagescores where image=ul.image) < ?
                            and ul.image not in (select image from likes where userid=?)
                            order by (select score from imagescores where image=ul.image)
                            limit ?''',
                            [ config.get('freshCeil'), session['userid'], config.get('perPage') ] )
            else:
                msg = Database.query('''select image from uploads ul
                            where (select score from imagescores where image=ul.image) < ?
                            order by (select score from imagescores where image=ul.image)
                            limit ?''',
                            [ config.get('freshCeil'), config.get('perPage') ] )

            l = [image(f['image']) for f in msg]
            return l

        
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        if g.user:
            msg = Database.query('''select caption, image, image_url from uploads ul
                        where (select score from imagescores where image=ul.image) < ?
                        and (select score from imagescores where image=ul.image) < ?
                        and ul.image not in (select image from likes where userid=?)
                        order by (select score from imagescores where image=ul.image)
                        limit ?''',
                        [ config.get('freshCeil'), score, session['userid'], config.get('perPage') ] )
        else:
            msg = Database.query('''select caption, image, image_url from uploads ul
                        where (select score from imagescores where image=ul.image) < ?
                        and (select score from imagescores where image=ul.image) < ?
                        order by (select score from imagescores where image=ul.image)
                        limit ?''',
                        [ config.get('freshCeil'), score, config.get('perPage') ] )



        l = [image(f['image']) for f in msg]
        return msg

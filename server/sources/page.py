from flask import request, session, g
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
        return jsonify([{'image_url':f.imageURL, 'caption':f.caption, 'score': f.score} for f in msg])

    def generateHot(self):
        after = self.request.args.get('after')
        if after is None:
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
                
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

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
        a = set()
        [a.add(f.permID) for f in hot]
        [a.add(f.permID) for f in recs]
        l = [f for f in a]
        random.shuffle(l)
        random.shuffle(l)
        l = [image(f) for f in l]
        return l
        
    def generateTrending(self):
        after = self.request.args.get('after')
        if after is None:
            msg = Database.query('''select caption, image, image_url from Uploads ul 
                    where (select score from imagescores where image=ul.image) < ? 
                    and (select score from imagescores where image=ul.image) > ? 
                    order by (select score from imagescores where image=ul.image) 
                    limit ?''', 
                    [ config.get('trendingCeil'), config.get('trendingFloor'), config.get('perPage') ] )
            return msg
        

        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        msg = Database.query('''select caption, image, image_url from uploads ul
                    where (select score from imagescores where image=ul.image) < ?
                    and (select score from imagescores where image=ul.image) > ?
                    and (select score from imagescores where image=ul.image) < ?
                    order by (select score from imagescores where image=ul.image)
                    limit ?''',
                    [ config.get('trendingCeil'), config.get('trendingFloor'), score, config.get('perPage') ] )
        
        return msg

    #TODO: for fresh, consider ordering based solely on upload date
    def generateFresh(self):
        after = self.request.args.get('after')
        if after is None:
            msg = Database.query('''select image from uploads ul
                        where (select score from imagescores where image=ul.image) < ?
                        order by (select score from imagescores where image=ul.image)
                        limit ?''',
                        [ config.get('freshCeil'), config.get('perPage') ] )
            l = [image(f['image']) for f in msg]
            return l

        
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        msg = Database.query('''select caption, image, image_url from uploads ul
        where (select score from imagescores where image=ul.image) < ?
        and (select score from imagescores where image=ul.image) < ?
        order by (select score from imagescores where image=ul.image)
        limit ?''',
        [ config.get('freshCeil'), score, config.get('perPage') ] )
        return msg

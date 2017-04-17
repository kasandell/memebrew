from flask import request, session
from config import config
from database import Database



class page(object):
    def __init__(self, request):
        self.request = request

    def __getPage(self):
        if session['page_title'] == 'hot':
            return self.generateHot()
        elif session['page_title'] == 'trending':
            return self.generateTrending()
        elif session['page_title'] == 'fresh':
            return self.generateFresh()
        else:
            return None

    def getPage(self):
        return self.__getPage()


        
    
    def getJSON(self):
        msg = self.__getPage()
        return jsonify([{'image_url':f['image_url'], 'caption':f['caption'], 'score': get_score(f['image'])} for f in self.msg])


    def generateHot(self):
        after = self.request.args.get('after')
        if after is None:
            msg = Database.query('''select caption, image, image_url from Uploads ul 
                    where (select score from imagescores where image=ul.image) > ? 
                    order by (select score from imagescores where image=ul.image) desc 
                    limit ?''', 
                    [ config.get('hotFloor'), config.get('perPage') ] )

            return msg
                
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        msg = Database.query('''select caption, image, image_url from uploads ul 
                where (select score from imagescores where image=ul.image) < ? 
                and (select score from imagescores where image=ul.image) > ? 
                order by (select score from imagescores where image=ul.image) desc 
                limit ?''', 
                [ score, config.get('hotFloor'), config.get('perPage')] )

        return msg

    
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
            msg = Database.query('''select caption, image, image_url from uploads ul
                        where (select score from imagescores where image=ul.image) < ?
                        order by (select score from imagescores where image=ul.image)
                        limit ?''',
                        [ config.get('freshCeil'), config.get('perPage') ] )
            return msg

        
        score = Database.query('select score from imagescores where image=?',
                [after], one=True)['score']

        msg = Database.query('''select caption, image, image_url from uploads ul
        where (select score from imagescores where image=ul.image) < ?
        and (select score from imagescores where image=ul.image) < ?
        order by (select score from imagescores where image=ul.image)
        limit ?''',
        [ config.get('freshCeil'), score, config.get('perPage') ] )
        return msg

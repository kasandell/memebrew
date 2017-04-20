#
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               Buddha bless the code
#


import uuid
import os
from werkzeug.utils import secure_filename
from operator import itemgetter
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5, sha256
from datetime import datetime
from math import log
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify, send_file
from sources.database import Database
from sources.image import image
from sources.util import utils
from sources.user import user
from sources.recommender import recommender
from sources.config import config
from sources.page import page


'''
lastXImages = 20
lastXUsers = 20
topXUsers = 10



freshFloor = 0
freshCeil = 10
trendingFloor = freshCeil
trendingCeil = 18
hotFloor = trendingCeil
'''


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOADS_FOLDER'] = config.get('uploadsFolder') 



#web interface
stylesheets = [f for f in os.listdir("static") if f.endswith('.css')]

# add all the stylesheets to the templates
@app.context_processor
def inject_stylesheets():
    return dict(stylesheets=stylesheets)

#set up everything that needs to happen before a request is made
@app.before_request
def before_request():
    g.user = None
    if 'userid' in session:
        g.user = Database.query('select * from users where userid = ?', [session['userid']], one=True)


#log a user in
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('hot'))
    error = None
    if request.method == 'POST':
        user = Database.query('SELECT * FROM Users WHERE username=?', [request.form['username']], one=True)
        if user is None:
            error = 'Username not found'
        elif str(sha256(request.form['password']).hexdigest()) != str(user['passhash']):
            error = 'Incorrect password'
        else:
            flash('You were logged in')
            session['logged_in'] = True
            session['userid'] = user['userid']
            return redirect(url_for('hot'))
    return render_template('login.html', error=error)



#log user out
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    flash('You were logged out')
    session.pop('userid', None)
    session['logged_in'] = False
    return redirect(url_for('login'))


#get a user's unique id, given their username
def get_user_id(uname):
    user = Database.query('select userid from Users where username=?', [uname], one=True)
    return user[0] if user else None



#register a new user
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('hot'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You must enter a username'
        elif not request.form['password']:
            error = 'You must enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords must match'
        elif get_user_id(request.form['username']) is not None:
            error = 'That username is already taken'
        else:
            v = str(uuid.uuid1())
            #insert user
            Database.execute('insert into Users(userid, username, passhash) VALUES(?,?,?)', [v ,str(request.form['username']), str(sha256(request.form['password']).hexdigest())])

            flash('Your account was created, you may log in now')
            return redirect(url_for('login'))
    return render_template('register.html', error = error)



#redirect a user to the hot page
@app.route('/', methods = ['GET'])
def base_page():
    return redirect(url_for('hot'))


#hot page
@app.route('/hot', methods = ['GET'])
def hot():
    '''
    print config.get('databaseLocation')
    session['page_title'] = 'hot'
    after = request.args.get('after')
    if after is None:
        msg = Database.query('select caption, image, image_url from Uploads ul order by (select score from imagescores where image=ul.image) desc')
        return render_template('meme_pages.html', messages = msg)

    score = Database.query('select score from imagescores where image=?', [after], one=True)['score']
    msg = Database.query('select caption, image, image_url from uploads ul where (select score from imagescores where image=ul.image) < ? order by (select score from imagescores where image=ul.image) desc limit ?', [score, config.get('PER_PAGE')])
    '''
    session['page_title'] = 'hot'
    p = page(request)
    msg = p.getPage()
    return render_template('meme_pages.html', messages = msg) 


#api endpoint for hot, used by app
@app.route('/api/hot', methods = ['GET'])
def api_hot():
    session['page_title'] = 'hot'
    '''
    after = request.args.get('after')
    if after is None:
        msg = Database.query('select caption, image, image_url from Uploads ul order by (select score from imagescores where image=ul.image) desc')
        return render_template('meme_pages.html', messages = msg)

    score = Database.query('select score from imagescores where image=?', [after], one=True)['score']
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption'], 'score': get_score(f['image'])} for f in msg])
    '''
    p = page(request)
    return p.getJSON()




#trending page
#TODO: rewrite to be images with most upvotes/time frame 
#TODO: consider something like a controversial page
@app.route('/trending', methods = ['GET'])
def trending():
    session['page_title'] = 'trending'
    '''
    msg = Database.query('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [trendingFloor, trendingCeil])
    return render_template('meme_pages.html', messages = msg) 
    '''
    p = page(request)
    msg = p.getPage()
    return render_template('meme_pages.html', messages = msg) 






#trending api endpoint, used by app
@app.route('/api/trending', methods = ['GET'])
def api_trending():
    session['page_title'] = 'trending'
    '''
    msg = Databse.query('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [trendingFloor, trendingCeil])
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption'], 'score': get_score(f['image'])} for f in msg])
    '''

    p = page(request)
    return p.getJSON()




#recommended page
@app.route('/recommended', methods = ['GET'])
def recommended(): 
    session['page_title'] = 'recommended'
    rc = recommender( session['userid'] )
    recs = rc.getRecommendations()
    r = [ f.jsonify() for f in recs]
    return render_template('meme_pages.html', messages = r)


#api recommended, used by app
@app.route('/api/recommended', methods = ['GET'])
def api_recommended():
    session['page_title'] = 'recommended'
    rc = recommender( session['userid'] )
    recs = rc.getRecommendations()
    r = [ f.jsonify() for f in recs]
    return render_template('meme_pages.html', messages = r)




#fresh page, images order by upload time
@app.route('/fresh', methods = ['GET'])
def fresh():
    session['page_title'] = 'fresh'
    '''
    msg = Database.query('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [freshFloor, freshCeil])
    for m in msg:
        print str(m['image_url'])
    '''
    p = page(request)
    msg = p.getPage()
    return render_template('meme_pages.html', messages = msg) 



#fresh api, used by app
@app.route('/api/fresh', methods = ['GET'])
def api_fresh():
    session['page_title'] = 'fresh'
    '''
    msg = Database.query('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [freshFloor, freshCeil])
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption']} for f in msg])
    '''
    p = page(request)
    return p.getJSON()





'''
summary: if we've already liked image, ignore the rest of the method
if not, say that we like it
if we've disliked it, remove from dislikes
update the score
for every tag
if we've never seen the tag, give it a starting score
else, update the score
if we've liked/disliked the image before, update the opposite table to represent the loss of 1 for that tag
'''
#TODO: fix db state to work without update on duplicate since we insert it on upload
@app.route('/<perm_id>/like', methods = ['POST'])
#user like image, update score and database entries
def like_image(perm_id):
    print 'like'
    u = user( session[ 'userid' ])
    i = image(perm_id)
    u.likeImage(i)
    return jsonify({'success':True})
    


@app.route('/<perm_id>/dislike', methods = ['POST'])
#user dislike an image, update image score, and database entries
def dislike_image(perm_id):
    print 'dislike'
    u = user( session[ 'userid' ])
    i = image(perm_id)
    u.dislikeImage(i)
    return jsonify({'success':True})




#TODO: make this
#upload images
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if not g.user:
        flash('You need to be signed in to upload')
        return redirect(url_for('hot'))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload'))
        fl = request.files['file']
        if fl.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))
        if fl and utils.allowedFile(fl.filename):
            img = image(request)
            return redirect(url_for('fresh'))

    return render_template('upload.html')



@app.route('/img/<perm_id>', methods = ['GET'])
def retImg(perm_id):
    print app.config['UPLOADS_FOLDER']
    #TODO: make some way to make sure they can only access what's in uploads directory
    if os.path.exists(app.config['UPLOADS_FOLDER'] + '/' + perm_id):
        type = utils.getImageType(perm_id)
        mt = None
        if type == '.jpeg' or type == '.jpg':
            mt = 'image/jpeg'
        elif type == '.png':
            mt = 'image/png'
        else:
            mt = 'image/gif'
        return send_file( (app.config['UPLOADS_FOLDER'] + '/' + perm_id), mimetype=mt)

    return send_file( (app.config['UPLOADS_FOLDER'] + '/fnf.jpg'), mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()

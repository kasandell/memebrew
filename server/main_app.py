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
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5, sha256
from datetime import datetime
from math import log
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify

epoch = datetime(1970, 1, 1)

DATABASE = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/database/meme.db'
PER_PAGE = 30

lastXImages = 20


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DATABASE)
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


#given a username, return a dictionary from the database of their preferences towards certain kinds of images
#def get_user_prefs(user):





@app.before_request
def before_request():
    g.user = None
    if 'userid' in session:
        g.user = query_db('select * from Users where userid = ?',
        [session['userid']], one=True)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('hot'))
    error = None
    if request.method == 'POST':
        user = query_db('SELECT * FROM Users WHERE username=?', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif str(sha256(request.form['password']).hexdigest()) != str(user['passhash']):#TODO chnage this to be hash of password
            print str(sha256(request.form['password']).hexdigest()), user['passhash']
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['logged_in'] = True
            session['userid'] = user['userid']
            return redirect(url_for('hot'))
    return render_template('login.html', error=error)



@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('userid', None)
    session['logged_in'] = False
    return redirect(url_for('login'))


def get_user_id(uname):
    user = query_db('select userid from Users where username=?', [uname], one=True)
    return user[0] if user else None



@app.route('/register', methods = ['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('hot'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords must match'
        elif get_user_id(request.form['username']) is not None:
            error = 'That username is already taken'
        else:
            v = str(uuid.uuid1())
            print v
            print str(request.form['username'])
            print str(sha256(str(request.form['password'])).hexdigest())
            db = get_db()
            db.execute('insert into Users(userid, username, passhash) VALUES(?,?,?)', [v ,str(request.form['username']), str(sha256(request.form['password']).hexdigest())])
            db.commit()
            flash('Your account was created, you may log in now')
            return redirect(url_for('login'))
    return render_template('register.html', error = error)



@app.route('/', methods = ['GET'])
def base_page():
    return redirect(url_for('hot'))


#hot page
#accepts optional username, which filters what images the user sees, if they've already liked or disliked them 
@app.route('/hot', methods = ['GET'])
def hot():
    session['page_title'] = 'hot'
    after = request.args.get('after')
    recommend()
    if after is None:
        return render_template('meme_pages.html')

    #load the most popular current images


@app.route('/api/hot', methods = ['GET'])
def api_hot():
    session['page_title'] = 'hot'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return render_template('meme_pages.html', messages = msg) 



#trending page
#accepts optional username, which filters what images the user sees, if they've already liked or disliked them 
@app.route('/trending', methods = ['GET'])
def trending():
    session['page_title'] = 'trending'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return render_template('meme_pages.html', messages = msg) 





@app.route('/api/trending', methods = ['GET'])
def api_trending():
    session['page_title'] = 'trending'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return jsonify([{'image_url':f['image_url'], 'image':f['image'], 'score': get_score(f['image'])} for f in msg])




#recommended page
@app.route('/recommended', methods = ['GET'])
def recommended(): 
    session['page_title'] = 'recommended'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return jsonify([{'image_url':f['image_url'], 'image':f['image']} for f in msg])


@app.route('/api/recommended', methods = ['GET'])
def api_recommended():
    session['page_title'] = 'recommended'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return render_template('meme_pages.html', messages = msg) 




@app.route('/fresh', methods = ['GET'])
def fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return jsonify([{'image_url':f['image_url'], 'image':f['image']} for f in msg])



@app.route('/api/fresh', methods = ['GET'])
def api_fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return render_template('meme_pages.html', messages = msg) 



@app.route('/<perm_id>/like', methods = ['POST'])
def like_image(perm_id):
    db = get_db()
    db.execute('insert into Likes(userid, image) VALUES(?,?) WHERE not exists (select 1 from Likes where userid=? and image=?)', [session['userid'], str(perm_id), session['userid'], str(perm_id)])
    db.execute('delete from Dislikes(userid, image) VALUES(?,?)', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    db.execute('insert into ImageScores(image, score) VALUES(?,?) on duplicate key update score=VALUES(?)', [str(perm_id), float(val), float(val)])
    db.commit()
    


@app.route('/<perm_id>/dislike', methods = ['POST'])
def dislike_image(perm_id):
    db = get_db()
    db.execute('insert into Dislikes(userid, image) VALUES(?,?) WHERE not exists (select 1 from Dislikes where userid=? and image=?)', [session['userid'], str(perm_id), session['userid'], str(perm_id)])
    db.execute('delete from Likes(userid, image) VALUES(?,?)', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    db.execute('insert into ImageScores(image, score) VALUES(?,?) on duplicate key update score=VALUES(?)', [str(perm_id), float(val), float(val)])
    db.commit()


@app.route('/upload')
def upload():
    return redirect(url_for('hot'))


def secs_since_epoch(date):
    timeDelt = date-epoch
    return (td.days*86400) + td.seconds + (float(td.microseconds)/1000000)

def score(upvotes, downvotes):
    return ups-downs

def get_score(img):
    ups_q = query_db('select * from likes where image=?', [img])
    ups = len(ups_q)
    downs_q = query_db('select * from dislikes where image=?', [img])
    downs = len(ups_q)
    s = score(ups, downs)
    order = log(max(abs(s), 1), 10)
    sign = 1 if s > 0 else -1 if s < 0 else 0
    postDate_q = query_db('select strftime("%s", uploadtime) from uploads where image=?', [img], one=True)
    postDate = postaDate_q
    seconds = secs_since_epoch(date) - 1490215831 #yup just deal with my random timestamp sma
    return round(sign * order + seconds / 45000, 7)


def recommend():
    #take last x images liked by user, get all likers
    print 'recommend'
    print session['userid']
    print lastXImages
    past_images = query_db('select image from likes where userid=? limit ?', [session['userid'], lastXImages])
    users = []
    for img in past_images:
        print img

    #also we are going to find the most similar users based simply on their weights


    return 1



if __name__ == "__main__":
    app.run()

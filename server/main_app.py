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
from operator import itemgetter
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
lastXUsers = 20
topXUsers = 10


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#return the database
def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DATABASE)
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


#query our database
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv



#set up everything that needs to happen before a request is made
@app.before_request
def before_request():
    g.user = None
    if 'userid' in session:
        g.user = query_db('select * from Users where userid = ?',
        [session['userid']], one=True)


#log a user in
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



#log user out
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    flash('You were logged out')
    session.pop('userid', None)
    session['logged_in'] = False
    return redirect(url_for('login'))


#get a user's unique id, given their username
def get_user_id(uname):
    user = query_db('select userid from Users where username=?', [uname], one=True)
    return user[0] if user else None



#register a new user
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



#redirect a user to the hot page
@app.route('/', methods = ['GET'])
def base_page():
    return redirect(url_for('hot'))


#hot page
#accepts optional username, which filters what images the user sees, if they've already liked or disliked them 
@app.route('/hot', methods = ['GET'])
def hot():
    session['page_title'] = 'hot'
    after = request.args.get('after')
    if after is None:
        return render_template('meme_pages.html')

    #load the most popular current images


#api endpoint for hot, used by app
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
    print msg
    return render_template('meme_pages.html', messages = msg) 





#trending api endpoint, used by app
@app.route('/api/trending', methods = ['GET'])
def api_trending():
    session['page_title'] = 'trending'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return jsonify([{'image_url':f['image_url'], 'image':f['image'], 'score': get_score(f['image'])} for f in msg])




#recommended page
@app.route('/recommended', methods = ['GET'])
def recommended(): 
    session['page_title'] = 'recommended'
    recs = recommend()
    print recs
    return 'hi' 
    #return jsonify([{'image_url':f['image_url'], 'image':f['image']} for f in msg])


#api recommended, used by app
@app.route('/api/recommended', methods = ['GET'])
def api_recommended():
    session['page_title'] = 'recommended'
    recs = reccomend()
    print recs
    return 'hi'
    #return render_template('meme_pages.html', messages = msg) 




#fresh page, images order by upload time
@app.route('/fresh', methods = ['GET'])
def fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return render_template('meme_pages.html', messages = msg) 



#fresh api, used by app
@app.route('/api/fresh', methods = ['GET'])
def api_fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    return jsonify([{'image_url':f['image_url'], 'image':f['image']} for f in msg])



@app.route('/<perm_id>/like', methods = ['POST'])
#user like image, update score and database entries
def like_image(perm_id):
    db = get_db()
    db.execute('insert into Likes(userid, image) VALUES(?,?) WHERE not exists (select 1 from Likes where userid=? and image=?)', [session['userid'], str(perm_id), session['userid'], str(perm_id)])
    db.execute('delete from Dislikes(userid, image) VALUES(?,?)', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    db.execute('insert into ImageScores(image, score) VALUES(?,?) on duplicate key update score=VALUES(?)', [str(perm_id), float(val), float(val)])
    
    tagsForImage = query_db('select idnumber from imagetags where image=?', [perm_id])
    #for every tag, say that we like it more
    for tag in tagsForImage:
        t = tag['idnumber']
        db.execute('insert into tagLikes(userid, idnumber, count) VALUES(?,?, 1) on duplicate key update count = count+1', [session['userid'], int(t)])
    db.commit()
    


@app.route('/<perm_id>/dislike', methods = ['POST'])
#user dislike an image, update image score, and database entries
def dislike_image(perm_id):
    db = get_db()
    db.execute('insert into Dislikes(userid, image) VALUES(?,?) WHERE not exists (select 1 from Dislikes where userid=? and image=?)', [session['userid'], str(perm_id), session['userid'], str(perm_id)])
    db.execute('delete from Likes(userid, image) VALUES(?,?)', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    db.execute('insert into ImageScores(image, score) VALUES(?,?) on duplicate key update score=VALUES(?)', [str(perm_id), float(val), float(val)])
    tagsForImage = query_db('select idnumber from imagetags where image=?', [perm_id])
    #for every tag, say that we dislike it more
    for tag in tagsForImage:
        t = tag['idnumber']
        db.execute('insert into tagDislikes(userid, idnumber, count) VALUES(?,?, -1) on duplicate key update count = count-1', [session['userid'], int(t)]) 

    
    db.commit()


@app.route('/upload')
#TODO: make this
#upload images
def upload():
    return redirect(url_for('hot'))


#return seconds since epoch
def secs_since_epoch(date):
    timeDelt = date-epoch
    return (td.days*86400) + td.seconds + (float(td.microseconds)/1000000)

#calculate the difference between upvotes and downvotes
def score(upvotes, downvotes):
    return ups-downs

#calculate an image score, used for selecting into hot/trending
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


#recommend a list of images to the user
def recommend():
    #take last x images liked by user, get all likers
    past_images = query_db('select image from likes where userid=? limit ?', [session['userid'], lastXImages])
    uSet = set()
    #get users who've liked similar images
    for img in past_images:
        iName = img['image']
        unames = query_db('select userid from likes where (image=? and NOT userid=?) limit ? ', [iName, session['userid'], lastXUsers])
        [uSet.add(f['userid']) for f in unames]
    unames = [f for f in uSet]
    print unames
    weights = {}
    #get each user's weights towards an image
    for name in unames:
            weights[str(name)] = calculate(name)
    #select the most similar users to us
    mostPromisingUsers = [str(f[0]) for f in topMostPromising(weights)]
    imgs = getImagesFromPromising(mostPromisingUsers)
    return (imgs[:20] if len(imgs) >20 else imgs)



#given a list of promising users, take images they've liked that we haven't liked or disliked
#select the most likely images from the most promising users by using the euclidean distance between a user's preferences and an image weight
def getImagesFromPromising(promising):
    image = set()
    for user in promising:
        imgs = query_db('select image from likes l where userid=? and not exists(select 1 from likes i where userid=? and l.image != i.image)', [user, session['userid']])
        [image.add(f['image']) for f in imgs]
    #final images
    images = [f for f in image]
    #sort images based on their linear distance from the user's tags
    imgWeights = [(f, calcWeightDiff(image)) for f in images]
    imgWeights = sorted(imgWeights, key=itemgetter(1))
    return [f[0] for f in imgWeights]



#calculate the distance(or difference) between an image weight set and a user's weight set
def calcWeightDiff(image):
    weights = getImageWeights(image)
    userWeights = calculate(session['userid'])
    diff = float(eDist(weights, userWeights))
    return diff



#get all tags that an image represents
def getImageWeights(image):
    w = query_db('select idnumber from imagetags where image=?', [str(image)])
    weights = {}
    for we in w:
        weights[w['idnumber']] = 1
    return weights


    

#return the top most promising users, number defined by constant topXUsers
def topMostPromising(weights): #return the x most promising users
    dists = []
    userWeights = calculate(session['userid'])
    for w in weights:
        dists.append( (w, eDist(weights[w], userWeights)) )
    dists = sorted(dists, key=itemgetter(1))
    return (dists[:topXUsers] if len(dists) < topXUsers else dists)



#calculate linear distance between two weight sets
#TODO: make this so that it can deal with tags potentially not being present in a users bias set
#calculate euclidean distance between two weight sets
def eDist(w1, w2):
    #for tags not seen, potentially make their value default to -1 for images
    count = 0
    tagsSeen = set()
    for tag in w1:
        if tag in w2:
            count += float(square( (w1[tag] - w2[tag] ) ))
        else:
            count += float(square(w1[tag]))
        tagsSeen.add(tag)
    for tag in w2:
        if tag not in tagSeen:
            if tag in w1:
                count += float(square(w2[tag] - w1[tag]))
            else:
                count += float(square(w2[tag]))
    return count

#square a val, used for calculating euclidean distance
def square(val):
    return float(val*val)
        

#calculate the weights toward an image on a [-1, 1] scale
def calculate(name):#calculate weight toward image tags
    likes = query_db('select idnumber, count from taglikes where userid=?', [str(name)])
    dislikes = query_db('select idnumber, count from tagdislikes where userid=?', [str(name)])
    tags = set()
    for l in likes:
        tags.add(l['idnumber'])
    for d in dislikes:
        tags.add(d['idnumber'])

    tagWeights = {}
    
    for tag in tags:
        totalSeen = 0
        count = 0
        for l in likes:
            if l['idnumber'] == tag:
                totalSeen = totalSeen + int(l['count'])
                count = count + int(l['count'])
        for d in dislikes:
            if d['idnumber'] == tag:
                totalSeen = totalSeen + int(l['count'])
                count = count - int(l['count'])
        tagWeights[str(tag)] = float(count/totalSeen)
    return tagWeights
    

        







if __name__ == "__main__":
    app.run()

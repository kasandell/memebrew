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

epoch = datetime(1970, 1, 1)

DATABASE = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/database/meme.db'
PER_PAGE = 30
UPLOADS_FOLDER = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/server/storage/'
ALLOWED_EXTENSIONS = ['gif', 'png', 'jpeg', 'jpg']

baseImageDir = 'http://127.0.0.1:5000/img'


lastXImages = 20
lastXUsers = 20
topXUsers = 10



freshFloor = 0
freshCeil = 10
trendingFloor = freshCeil
trendingCeil = 18
hotFloor = trendingCeil


app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER

# add all the stylesheets to the templates
@app.context_processor
def inject_stylesheets():
    # maybe find a less acoustic way to do this, if you want
    files = ['messages.css', 'navigation.css', 'page.css', 'variables.css']
    return dict(stylesheets=files)

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            #print str(sha256(request.form['password']).hexdigest()), user['passhash']
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
            #print v
            #print str(request.form['username'])
            #print str(sha256(str(request.form['password'])).hexdigest())
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
    #after = request.args.get('after')
    #if after is None:
    #    return render_template('meme_pages.html')

    #load the most popular current images
    #msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ?) order by uploadtime desc', [hotFloor])
    msg = query_db('select caption, image, image_url from Uploads ul order by (select score from imagescores where image=ul.image) desc')
    print msg
    return render_template('meme_pages.html', messages = msg) 


#api endpoint for hot, used by app
@app.route('/api/hot', methods = ['GET'])
def api_hot():
    session['page_title'] = 'hot'
    #msg = query_db('select caption, image, image_url from Uploads order by uploadtime desc')#query_db('select uploads.image from Uploads order by uploads.uploadtime desc limit ?' [PER_PAGE])
    msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ?) order by uploadtime desc', [hotFloor])
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption'], 'score': get_score(f['image'])} for f in msg])



#trending page
#TODO: rewrite to be images with most upvotes/time frame 
#TODO: consider something like a controversial page
@app.route('/trending', methods = ['GET'])
def trending():
    session['page_title'] = 'trending'
    msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [trendingFloor, trendingCeil])
    return render_template('meme_pages.html', messages = msg) 





#trending api endpoint, used by app
@app.route('/api/trending', methods = ['GET'])
def api_trending():
    session['page_title'] = 'trending'
    msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [trendingFloor, trendingCeil])
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption'], 'score': get_score(f['image'])} for f in msg])




#recommended page
@app.route('/recommended', methods = ['GET'])
def recommended(): 
    session['page_title'] = 'recommended'
    recs = recommend()
    print recs
    return render_template('meme_pages.html', messages = recs)
    #return jsonify([{'image_url':f['image_url'], 'image':f['image']} for f in msg])


#api recommended, used by app
@app.route('/api/recommended', methods = ['GET'])
def api_recommended():
    session['page_title'] = 'recommended'
    recs = reccomend()
    return render_template('meme_pages.html', messages = recs)




#fresh page, images order by upload time
@app.route('/fresh', methods = ['GET'])
def fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [freshFloor, freshCeil])
    for m in msg:
        print str(m['image_url'])
    return render_template('meme_pages.html', messages = msg) 



#fresh api, used by app
@app.route('/api/fresh', methods = ['GET'])
def api_fresh():
    session['page_title'] = 'fresh'
    msg = query_db('select caption, image, image_url from Uploads ul where ( (select score from imagescores where image=ul.image limit 1) > ? and (select score from imagescores where image=ul.image limit 1) < ?) order by uploadtime desc', [freshFloor, freshCeil])
    return jsonify([{'image_url':f['image_url'], 'caption':f['caption']} for f in msg])





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
    print perm_id
    db = get_db()
    alreadyLiked = query_db('select 1 from likes where userid=? and image=?', [session['userid'], str(perm_id)])
    if alreadyLiked:
        print 'already liked'
        return jsonify({'success': False, 'reason':'Already liked image'})
    db.execute('insert into likes(userid, image) select ?,?', [session['userid'], str(perm_id)])
    seen = False
    previouslySeen = query_db('select 1 from dislikes where userid=? and image=?', [session['userid'], str(perm_id)])
    if previouslySeen:
        seen = True
        print 'we\'ve disliked this before'
    db.execute('delete from dislikes where userid=? and image=?', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    print val
    scoreExists = db.execute('select 1 from imagescores where image=?', [str(perm_id)])
    print 'sore exists'
    if scoreExists:
        db.execute('update imagescores set score=? where image=?', [float(val), str(perm_id)])
    else:
        db.execute('insert into imagescores(image, score) select ?,?', [str(perm_id), float(val)])
    
    tagsForImage = query_db('select idnumber from imagetags where image=?', [perm_id])
    #for every tag, say that we like it more
    for tag in tagsForImage:
        t = tag['idnumber']
        exists = query_db('select 1 from taglikes where userid=? and idnumber=?', [session['userid'], int(t)])
        if exists:
            #say we like it, and if we've already liked this image, remove 1 from the dislikes
            db.execute('update taglikes set count=count+1 where userid=? and idnumber=?', [session['userid'], int(t)])
            if seen:
                print 'saw it already'
                db.execute('update tagdislikes set count=count-1 where userid=? and idnumber=?', [session['userid'], int(t)])
        else:
            db.execute('insert into taglikes(userid, idnumber, count) select ?,?,?', [session['userid'], int(t), 1])
            if seen:
                print 'saw it already'
                db.execute('update tagdislikes set count=count-1 where userid=? and idnumber=?', [session['userid'], int(t)])

        #jdb.execute('insert into tagLikes(userid, idnumber, count) SELECT ?,?, 1 on duplicate key update count = count+1', [session['userid'], int(t)])
    db.commit()
    return jsonify({'success':True})
    


@app.route('/<perm_id>/dislike', methods = ['POST'])
#user dislike an image, update image score, and database entries
def dislike_image(perm_id):
    print 'dislike'
    db = get_db()
    alreadyLiked = query_db('select 1 from dislikes where userid=? and image=?', [session['userid'], str(perm_id)])
    if alreadyLiked:
        print 'already disliked'
        return jsonify({'success': False, 'reason':'Already disliked image'})
    db.execute('insert into dislikes(userid, image) select ?,?', [session['userid'], str(perm_id)])
    previouslySeen = query_db('select 1 from likes where userid=? and image=?', [session['userid'], str(perm_id)])
    seen = False
    if previouslySeen:
        seen = True
        print 'we\'ve liked this before'
    db.execute('delete from likes where userid=? and image=?', [session['userid'], str(perm_id)])
    val = get_score(str(perm_id))
    print val
    scoreExists = db.execute('select 1 from imagescores where image=?', [str(perm_id)])
    print 'score exists'
    if scoreExists:
        db.execute('update imagescores set score=? where image=?', [float(val), str(perm_id)])
    else:
        db.execute('insert into imagescores(image, score) select ?,?', [str(perm_id), float(val)])
    
    tagsForImage = query_db('select idnumber from imagetags where image=?', [perm_id])
    #for every tag, say that we like it more
    for tag in tagsForImage:
        t = tag['idnumber']
        exists = query_db('select 1 from tagdislikes where userid=? and idnumber=?', [session['userid'], int(t)])
        if exists:
            db.execute('update tagdislikes set count=count+1 where userid=? and idnumber=?', [session['userid'], int(t)])
            if seen:
                print 'saw it already'
                db.execute('update taglikes set count=count-1 where userid=? and idnumber=?', [session['userid'], int(t)])
        else:
            db.execute('insert into tagdislikes(userid, idnumber, count) select ?,?,?', [session['userid'], int(t), 1])
            if seen:
                print 'saw it already'
                db.execute('update taglikes set count=count-1 where userid=? and idnumber=?', [session['userid'], int(t)])

        #jdb.execute('insert into tagLikes(userid, idnumber, count) SELECT ?,?, 1 on duplicate key update count = count+1', [session['userid'], int(t)])
    db.commit()
    return jsonify({'success':True})

def getImageType(imgName):
    if imgName[-4:].lower() == '.jpg' or imgName[-4:].lower() == '.png' or imgName[-4:].lower() == '.gif':
        return imgName[-4:].lower()
    if imgName[-5:].lower() == '.jpeg':
        return imgName[-5:].lower()



def addToDatabase(imgName, tags, link, caption):
    db = get_db()
    db.execute('insert into uploads(image,image_url, caption) VALUES(?,?,?)', [imgName, link, caption])
    
    for tag in tags:
        db.execute('insert into tagmaps(tagname) SELECT ? where not exists(select 1 from tagmaps where tagname=?)', [tag, tag])
        val = query_db('select idnumber from tagmaps where tagname=?', [tag], one=True)['idnumber']
        #print val
        db.execute('insert into imagetags(image,idnumber) VALUES(?,?)', [imgName, int(val)])

    v = get_score(str(imgName))#XXX
    print v
    db.execute('insert into imagescores(image, score) select ?,?', [imgName, v])
    db.commit()



def getTags(tagStr):
    tgArr = tagStr.split(',')
    tgArr = [f.strip() for f in tgArr]
    tgArr = [str(f).lower() for f in tgArr if (f is not '' and f is not None)]
    return tgArr

#TODO: make this
#upload images
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload'))
        fl = request.files['file']
        if fl.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))
        if fl and allowed_file(fl.filename):
            hash = str(uuid.uuid1())
            #TODO: finish full upload stuffs
            #TODO: insert hash into images database
            #TODO: tag image 
            fname = hash + getImageType(fl.filename)
            link = baseImageDir + '/' + fname
            tags = getTags(request.form['tags'])
            addToDatabase(hash, tags, link, str(request.form['caption']))


            fl.save(os.path.join(app.config['UPLOADS_FOLDER'], fname))
            return redirect(url_for('fresh'))

    return render_template('upload.html')



@app.route('/img/<perm_id>', methods = ['GET'])
def retImg(perm_id):
    #TODO: make some way to make sure they can only access what's in uploads directory
    if os.path.exists(app.config['UPLOADS_FOLDER'] + '/' + perm_id):
        type = getImageType(perm_id)
        mt = None
        if type == '.jpeg' or type == '.jpg':
            mt = 'image/jpeg'
        elif type == '.png':
            mt = 'image/png'
        else:
            mt = 'image/gif'
        return send_file( (app.config['UPLOADS_FOLDER'] + '/' + perm_id), mimetype=mt)

    return send_file( (app.config['UPLOADS_FOLDER'] + '/fnf.jpg'), mimetype='image/jpeg')

    

#return seconds since epoch
def secs_since_epoch(date):
    timeDelt = datetime.fromtimestamp(date)-epoch
    return (timeDelt.days*86400) + timeDelt.seconds + (float(timeDelt.microseconds)/1000000)

#calculate the difference between upvotes and downvotes
def score(upvotes, downvotes):
    return upvotes-downvotes

#calculate an image score, used for selecting into hot/trending
def get_score(img):
    print 'image:', img
    ups_q = query_db('select * from likes where image=?', [img])
    ups=0
    for up in ups_q:
        ups = ups+1
        print up['userid']
    print 'ups: ', ups
    downs_q = query_db('select * from dislikes where image=?', [img])
    downs = 0
    for down in downs_q:
        downs = downs + 1
        print down['userid']
    print 'downs: ' , downs
    print ups, downs
    s = score(ups, downs)
    order = log(max(abs(s), 1), 10)
    sign = 1 if s > 0 else -1 if s < 0 else 0
    postDate_q = query_db('select strftime("%s", uploadtime) from uploads where image=?', [img], one=True)
    postDate = int(postDate_q[0])
    seconds = secs_since_epoch(postDate) - 1490215831 #yup just deal with my random timestamp sma
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
    print 'usernames: ', unames
    weights = {}
    #get each user's weights towards an image
    for name in unames:
            weights[str(name)] = calculate(name)
    print 'weights', weights
    #select the most similar users to us
    mostPromisingUsers = [str(f[0]) for f in topMostPromising(weights)]
    print 'promising users:', mostPromisingUsers
    imgs = getImagesFromPromising(mostPromisingUsers)
    msgs = []
    for img in imgs:
        q = query_db('select caption, image, image_url from Uploads where image=?', [img], one=True) 
        msgs.append(q)
    return (msgs[:20] if len(msgs) >20 else msgs)



#given a list of promising users, take images they've liked that we haven't liked or disliked
#select the most likely images from the most promising users by using the euclidean distance between a user's preferences and an image weight
def getImagesFromPromising(promising):
    image = set()
    userLikes = query_db('select image from  likes where userid=?', [session['userid']])
    userSet = set()
    [userSet.add(f['image']) for f in userLikes]
    print userSet

    for user in promising:
        #imgs = query_db('select image from likes l where userid=? and not exists(select 1 from likes i where userid=? and l.image != i.image)', [user, session['userid']])

        otherLikes = query_db('select image from  likes where userid=?', [user])
        oLikes = [f['image'] for f in otherLikes]
        print 'other user likes: ', oLikes
        difLikes = [x for x in oLikes if x not in userSet]
        print difLikes
        [image.add(f) for f in difLikes]



    images = [f for f in image]
    print 'imgs: ', images
    #HERE
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
    print 'userWeights: ', userWeights
    for w in weights:
        dists.append( (w, eDist(weights[w], userWeights)) )
    print 'dists: ', dists
    dists = sorted(dists, key=itemgetter(1))
    print 'sorted dists', dists
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
        if tag not in tagsSeen:
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
                totalSeen = totalSeen + int(d['count'])
                count = count - int(d['count'])
        tagWeights[str(tag)] = float(count/totalSeen)
    return tagWeights
    

        







if __name__ == "__main__":
    app.run()

from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_user.signals import user_registered
from json import dumps, loads
import sqlite3
import string 
import random
import pprint

app = Flask(__name__)

class ConfigClass(object):
    SECRET_KEY = 'p\xe3\\l\xd5\xee\\6\xaa\xc4\xbc\xd0n\x95\xea\xfe\x00z\x82[t\x1bs\x85? \xe11\x98\xf9\xda@\x83\x1f\xa0"\xa3\xdf\xe1z\xe6R\xcc/\xafM5z\xdcY\xbe\xa9tqvj\x85\xe4\xe1\xaf\x9b\x07\x88.'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///static/db/flicks.db'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Flicks"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False        # Enable email authentication
    USER_ENABLE_USERNAME = True    # Disable username authentication

app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

user_manager = UserManager(app, db, User)
db.create_all()


# * Test route
@app.route('/',methods=['GET'])
@login_required
def home():
    return redirect(url_for('discover'))
    # return render_template('index.html')

@app.route('/discover', methods=['GET'])
@login_required
def discover():
    return render_template('discover.html')

@app.route('/results', methods=['GET'])
@login_required
def results():
    code = request.args.get('code',None)
    if(code is None):
        return 'error'
    c = connect()
    recs = groupsuggest(code)
    top3 = []
    for id in recs:
        c.execute("Select primary_title, start_year from title_basics where title_id = (?)", id)
        results = c.fetchone()
        primary_title = results[0]
        start_year = results[1]
        top3.append({"primary_title": primary_title, "start_year": start_year, "id": id})
    disconnect(c)
    return render_template('results.html', top3=top3)

@app.route('/gcreate', methods=['GET'])
@login_required
def gcreate():
    c = connect()
    found = True
    while(found == True):
        code = generateString()
        c.execute('select * from groups where code = ?', (code,))
        res = c.fetchone()
        if(res is None):
            found = False
    users = [current_user.id]
    c.execute('insert into groups (code, users) values (?, ?)', (code,dumps(users)))
    c.execute('select groups from attributes where user_id =(?)', (current_user.id,))
    groups = loads(c.fetchone()[0])
    if(len(groups) != 0):
        for v in groups:
            c.execute('delete from groups where code=(?)', (v,))
    groups = [code]
    print(dumps(groups))
    c.execute('update attributes set groups=(?) where user_id=(?)', (dumps(groups), current_user.id))
    disconnect(c)
    return render_template('gcreate.html',code=code, person=current_user.username)

@app.route('/gjoin', methods=['GET'])
@login_required
def gjoin():
    return render_template('gjoin.html')

@app.route('/joinsuccess', methods=['GET'])
@login_required
def joinsuccess():
    return render_template('joinsuccess.html')

@app.route('/search', methods=['GET'])
@login_required
def search():
    return render_template('search.html')

@app.route('/searchresults', methods=['GET'])
@login_required
def searchresults():
    return render_template('searchresults.html')

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    c = connect()
    user_id = (current_user.id,)
    c.execute('SELECT * FROM attributes WHERE user_id=?',user_id)
    print(c.fetchone())
    return render_template('profile.html', username=current_user.username)
    disconnect()

@app.route('/testing')
@login_required
def testing():
    ret = indivsuggest(current_user.id)
    return dumps(ret)

# region AJAX

@app.route('/join-group', methods=['POST'])
@login_required
def join_group():
    code = request.args.get('code',None)
    if(code is None):
        return 'error code 1'
    c = connect()
    c.execute('select users from groups where code=(?)',(code,))
    res = c.fetchone()
    if(res is None):
        disconnect(c)
        return 'error code 2'
    users = loads(res[0])
    users.append(current_user.id)
    c.execute('update groups set users=(?) where code=(?)', (dumps(users), code))
    c.execute('select groups from attributes where user_id=(?)', (current_user.id,))
    groups = loads(c.fetchone()[0])
    if(groups is None):
        groups = [code]
    else:
        groups.append(code)
    c.execute('update attributes set groups=(?) where user_id=(?)', (dumps(groups), current_user.id))
    disconnect(c)
    return 'success' 

@app.route('/check-people', methods=['GET'])
@login_required
def check_people():
    code = request.args.get('code',None)
    if(code is None):
        return 'error code 1'
    c = connect()
    c.execute('select users from groups where code=(?)',(code,))
    res = c.fetchone()
    if(res is None):
        disconnect(c)
        return 'error code 2'
    users = loads(res[0])
    usernames = []
    for v in users:
        if(v == current_user.id):
            continue
        c.execute('select username from users where id=(?)',(v,))
        res = c.fetchone()
        if(res is None):
            return 'error code 3'
        usernames.append(res)
    disconnect(c)
    return dumps(usernames)

@app.route('/discover-update', methods=['GET'])
@login_required
def discoverUpdate():
    ret = []
    c = connect()
    movies = indivsuggest(current_user.id)
    for e in movies:
        c.execute('select primary_title, genres from title_basics where title_id=(?)',(e[0],))
        movie = c.fetchone()
        ret.append({'title': movie[0], 'genre': movie[1], 'rating': 6.5, 'description': '<a>yeet</a>'})

    return dumps(ret)

# endregion

# region Utility Functions

def connect():
    sql = sqlite3.connect('static/db/flicks.db', isolation_level=None)
    c = sql.cursor()
    return c

def disconnect(c):
    try:
        c.close()
    except:
        print('Oops!')

def generateString():
    # initializing size of string  
    N = 4
    
    # using random.choices() 
    # generating random strings  
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k = N))
    return res

def swipeupdate(userid, movieid):
    c = connect()
    c.execute("select start_year, genres from title_basics where title_id = ?", (movieid,))
    movie = c.fetchone()
    if(movie is None):
        return 'error'

    c.execute("select director, genre, year, movies_swiped from attributes where user_id = ?", (userid,))
    useratt = c.fetchone()
    if(useratt is None):
        return 'error'

    start_year = movie[0]
    genres = movie[1].split(',')
    directors = []
    user_directors = loads(useratt[0])
    user_genres = loads(useratt[1])
    user_start_years = loads(useratt[2])
    movies_swiped = loads(useratt[3])

    genre_ret = user_genres
    director_ret = user_directors
    start_year_ret = user_start_years

    for genre in genres:
        checkTrue = 0
        for selectedgenre, weight in user_genres.items():
            if(selectedgenre == genre):
                genre_ret[genre] += 1
                checkTrue += 1
        if(checkTrue == 0):
            genre_ret[genre] = 1
            
    checkTrueY = 0
    for selectedyear, weight in user_start_years.items():
        if (int(selectedyear) == start_year):
            start_year_ret[selectedyear] += 1
            checkTrueY += 1
    if checkTrueY == 0:
        start_year_ret[start_year] = 1

    for director in directors:
        checkTrue = 0
        for selecteddirector, weight in user_directors.items():
            if(selecteddirector == director):
                director_ret[director] += 1
                checkTrue += 1
        if(checkTrue == 0):
            director_ret[director] = 1

    movies_swiped.append(movieid)
    c.execute('update attributes set genre=(?),director=(?),year=(?),movies_swiped=(?) where user_id=(?)',(dumps(genre_ret),dumps(director_ret),dumps(start_year_ret),dumps(movies_swiped),userid))
    disconnect(c)

def indivsuggest(UserID):
    GenV = 1
    DirV = 1
    YearV = 1
    RatM = 1
    
    c = connect()
    d = connect()
    c.execute("select director, genre, year, movies_swiped from attributes where user_id = ?", (UserID,))
    useratt = c.fetchone()
    c.execute("select title_id, start_year, genres from title_basics")
    movie = c.fetchone()
    movieratings = d.execute("select title_id, average_rating from title_ratings")
    
    user_directors = loads(useratt[0])
    user_genres = loads(useratt[1])
    user_start_years = loads(useratt[2])
    user_swiped = loads(useratt[3])
    
    dirmax = max(user_directors.values())
    genremax = max(user_genres.values())
    yearmax = max(user_start_years.values())

    scoreranking = {}
    while movie is not None:
        title_id = movie[0]
        start_year = movie[1]
        genres = movie[2].split(',')
        directors = []
        MovieScore = 1
        # normalize weights somehow 
        if(title_id in user_swiped):
            movie=c.fetchone()
            continue

        if(start_year == "\\N"):
            movie=c.fetchone()
            continue

        dirweight = 0
        genreweight = 0 
        yearweight = 0 

        for director, weight in user_directors.items(): 
            if director in directors:
                dirweight += weight/dirmax
                
        for genre, weight in user_genres.items(): 
            if genre in genres:
                genreweight += weight/genremax
                
        for year, weight in user_start_years.items():
            if int(year) == start_year:
                yearweight += weight/yearmax
                
        MovieScore = dirweight/len(user_directors)*DirV + genreweight/len(user_genres)*GenV + yearweight/len(user_start_years)*YearV
        # moviescore max is GenV + DirV + YearV
        
        d.execute('select average_rating from title_ratings where title_id=(?)',(title_id,))
        rating = d.fetchone()
        if(rating is None):
            movie=c.fetchone()
            continue

        av_r = rating[0]
        scoreranking[title_id] = MovieScore + (start_year/2020) + (av_r/10 * RatM)

        movie=c.fetchone()
        
    sort = sorted(scoreranking.items(), key=lambda k: k[1], reverse=True)
    del sort[10:]
    disconnect(c)
    disconnect(d)
    return sort
    # ["tt0000009", "tt0000335", "tt0000502", "tt0000574", "tt0000615", "tt0000630", "tt0000675", "tt0000676", "tt0000679", "tt0000739"]

def groupsuggest(groupcode):

    GenV = 1
    DirV = 1
    YearV = 1
    RatM = 1
    
    c = connect()
    d = connect()

    c.execute('select director, genre, year, movies_swiped from attributes where user_id in (select users from groups where code = ?)', groupcode) 
    useratt = c.fetchone()
    c.execute("select title_id, start_year, genres from title_basics")
    movie = c.fetchone()
    movieratings = d.execute("select title_id, average_rating from title_ratings")
    
    user_directors = loads(useratt[0])
    user_genres = loads(useratt[1])
    user_start_years = loads(useratt[2])
    user_swiped = loads(useratt[3])
    
    dirmax = max(user_directors.values())
    genremax = max(user_genres.values())
    yearmax = max(user_start_years.values())

    scoreranking = {}
    while movie is not None:
        title_id = movie[0]
        start_year = movie[1]
        genres = movie[2].split(',')
        directors = []
        MovieScore = 1
        # normalize weights somehow 
        if(title_id in user_swiped):
            movie=c.fetchone()
            continue

        if(start_year == "\n"):
            movie=c.fetchone()
            continue

        dirweight = 0
        genreweight = 0 
        yearweight = 0 

        for director, weight in user_directors.items(): 
            if director in directors:
                dirweight += weight/dirmax
                
        for genre, weight in user_genres.items(): 
            if genre in genres:
                genreweight += weight/genremax
                
        for year, weight in user_start_years.items():
            if int(year) == start_year:
                yearweight += weight/yearmax
                
        MovieScore += dirweight/len(user_directors)*DirV + genreweight/len(user_genres)*GenV + yearweight/len(user_start_years)*YearV
        # moviescore max is GenV + DirV + YearV
        
        d.execute('select average_rating from title_ratings where title_id=(?)',(title_id,))
        rating = d.fetchone()
        if(rating is None):
            movie=c.fetchone()
            continue
        
        av_r = rating[0]
        scoreranking[title_id] = MovieScore + (start_year/2020) + (av_r/10 * RatM)

        movie=c.fetchone()
    # movie_id movie title genre year release 
    sort = sorted(scoreranking.items(), key=lambda k: k[1], reverse=True)
    del sort[3:]
    disconnect(c)
    disconnect(d)
    return [a_tuple[0] for a_tuple in sort]
    # ["tt0000009", "tt0000335", "tt0000502", "tt0000574", "tt0000615", "tt0000630", "tt0000675", "tt0000676", "tt0000679", "tt0000739"]

# endregion

# region Event Handlers

@user_registered.connect_via(app)
def track_registration(sender, user, **extra):
    c = connect()
    user_id = user.id
    c.execute('INSERT into attributes (user_id,groups) VALUES (?,?)',(user_id,dumps([])))
    disconnect(c)

# endregion

# region SQL Queries
# endregion
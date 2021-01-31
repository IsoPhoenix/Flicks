def indivsuggest(UserID):
    GenV = 1
    DirV = 1
    YearV = 1
    RatM = 2
    
    c = connect()
    userlist = c.execute("select director, genre, year from attributes where user_id = ?", UserID)
    movielist = c.execute("select title_id, start_year, genres from title_basics")
    movieratings = c.execute("select title_id, average_rating from title_ratings")
    
    useratt = userlist.fetchone()
    user_directors = loads(useratt[0])
    user_genres = loads(useratt[1])
    user_start_years = loads(useratt[2])
    
    movie = movielist.fetchone()
    
    scoreranking = {}
    while movie is not None:
        title_id = movie[0]
        start_year = movie[1]
        genres = movie[2].split(',')
        directors = []
        MovieScore = 0

        for director, weight in user_directors.items(): 
            if director in directors:
                MovieScore += weight * DirV
        for genre, weight in user_genres.items(): 
            if genre in genres:
                MovieScore += weight * GenV
        for year, weight in user_start_years.items(): 
            if year == start_year:
                MovieScore += weight * YearV
        scoreranking[title_id] = MovieScore
    sort = sorted(scoreranking, key=lambda k: k[1])
    ret = dict(itertools.islice(sort.items(),3))
    disconnect(c)
    return ret
        
        
                
            



def groupsuggest(groupcode):
    c = connect()
    userlist = c.execute('select director, genre, year, movies_seen, movies_swiped from attributes where user_id in (select users from groups where code = ?)', groupcode) 
                # TODO: Fix fetching users from database, because Dylan said it's stored as a string
    NewUserID = Make a new User #TODO: Make a new user
    for user in userlist:
        total = int(user[movies_seen]) + int(user[movies_swiped])
        for category in user.items(): #TODO Don't know if .items() is appropriate here
            #TODO: Pseudocode begins here
            for item in category:
                scaleditem = item / total
                Append/add item value to NewUser (This has to take into account whether the item is already in newuser) #TODO: add item to newuser
    disconnect(c)
    return indivsuggest(NewUserID)
    # Ther eMight be a better/easier idea than making a new user here.
                



    
    

def groupsuggest(groupcode):
    c = connect()
    c.execute('select director, genre, year, movies_swiped from attributes where user_id in (select users from groups where code = ?)', groupcode) 
    userlist = c.fetchone()

    newuser_directors = {}
    newuser_genres = {}
    newuser_years = {}

    while userlist is not None:
        
        user_directors = loads(useratt[0])
        user_genres = loads(useratt[1])
        user_start_years = loads(useratt[2])
        movies_swiped = loads(useratt[3])
        
        for director, weight in user_directors.items():
            if director in newuser_directors:
                newuser_directors[director] += weight / movies_swiped
            else:
                newuser_directors[director] = weight / movies_swiped
            
        for genre, weight in user_genres.items(): 
            if genre in newuser_genres:
                newuser_genres[genre] += weight / movies_swiped
            else:
                newuser_genres[genre] = weight
        for year, weight in user_start_years.items():
            if year in newuser_years:
                newuser_years[year] += weight / movies_swiped
            else:
                newuser_genres[year] = weight / movies_swiped
        userlist = c.fetchone()   
    
    





for user in group:
    for each category in user:
        Divide all values by lowest value in category OR divide by sum of movies seen+swiped. Where does movies seen come from?
        Add to running sum in dict
    
Run algorithm on resulting dict


# merge users into 1 for group

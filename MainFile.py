#!/usr/bin/env python3
from flask import redirect, url_for,render_template,flash,request
from flask_login import login_user, current_user,logout_user
from datetime import datetime
from forms import *
import requests
from Auth import *
from datetime import datetime
from Positions import *
from Refresh import RefreshT,RefreshTid
from initializers import *
from User import *
from Threshholds import *
from Friends import *
from Market import *
from Favorites import *
import random
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

with app.app_context():
    db.create_all()
    

def AddThreshholds(TopThresh,BotThresh,symbol,Quantity):
        Threshhold = Threshholds(TopThresh =TopThresh,BotThresh = BotThresh, id = current_user.id ,Quantity = Quantity,symbol=symbol )
        db.session.add(Threshhold)
        db.session.commit()
    



def GetTdData(StockName,accessToken):
        url = "https://api.tdameritrade.com/v1/marketdata/"+StockName.upper()+"/quotes"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer " + accessToken
        request = requests.get(url,headers=headers)
        TDdata = request.json()
        return TDdata

def CheckAndActionThreshHolds():
    with app.app_context():
        print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
        print("Function To Check For Threshholds to Sell")
        tempPrices = dict() #used so the same symbol isnt loaded multiple times
        ToCheck = Threshholds.query.all()
        for Stock in ToCheck:
            tempPrice = tempPrices.get(Stock.symbol,None)
            UserToUpdate = User.query.filter_by(id = Stock.id).first()
            if tempPrice == None:
                RefreshTid(UserToUpdate.id)
                tempPrices[Stock.symbol] =  GetTdData(Stock.symbol,UserToUpdate.access_token)[Stock.symbol]['askPrice']
                tempPrice = tempPrices[Stock.symbol]
            print(tempPrice)                    
            if tempPrice < Stock.BotThresh or tempPrice > Stock.TopThresh:
                print("threshhold passed, selling " +Stock.symbol )
                Sell(Stock.symbol,str(Stock.Quantity),UserToUpdate)
                Threshholds.query.filter_by(index = Stock.index).delete()
        db.session.commit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(CheckAndActionThreshHolds,'interval',seconds=30)
sched.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def index():
    return redirect(url_for('home'))
    
@app.route("/sell/<Stock>",methods=("POST","GET"))
def SellStock(Stock):
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    Quanitiy = request.args.get('Quanitiy')
    if int(Quanitiy)>int(GetMaxQuantity(Stock)):
        flash("Selling More Stocks than Owned")
        return redirect(url_for('Positions'))
    Sell(Stock,Quanitiy,current_user)
    return redirect(url_for('Positions'))

@app.route("/order/<Stock>",methods=("POST","GET"))
def Order(Stock):
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    if current_user.access_token == "":
        flash("Connect An Account Before Buying")
        return redirect(url_for('Market'))
    Quanitiy = request.args.get('Quanitiy')
    Buy(Stock,Quanitiy,current_user)
    return redirect(url_for('Positions'))

@app.route("/home")
def home():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    
    if ((current_user.access_token!="") == False): #If TD Account is not connected you need to connect it before proceeding to home page
        return redirect(url_for('Profile'))
        
    # positions = GetPositions() #(Quantity, avg price paid, current price, asset name) #USE FOR USER DATA
    positions  = [[],[3,200,10,'TSLA'],[2,230,100,'AAPL'],[10,80,10,'META'],[2,150,150,'AMZN'],[6,125,110,'AMD'],[20,100,90,'NVDA']] #USE FOR SAMPLE DATA
    quantity, avg_price, current_price, asset_name,percentage_of_assets,init_times,init_values,init_color = [],[],[],[],[],[],[],''
    if len(positions) == 0 or positions[0] == -1: #account has no positions
        quantity.append(0)
        avg_price.append(0)
        current_price.append(0)
        asset_name.append('NO ASSETS')
        percentage_of_assets.append(0)
        init_times.append(0)
        init_values.append(0)
        init_color = 'rgb(0,0,0)' 
    else:
        for i in positions[1:]: #acount has positions
            quantity.append(i[0])
            avg_price.append(i[1])
            current_price.append(i[2])
            asset_name.append(i[3])
        percentage_of_assets = getPercentage(avg_price, quantity)
        init_times_values = get_1days_time_values(asset_name,quantity) #init_times_values = get_1days_time_values(asset_name,quantity)
        init_times = init_times_values[0]
        init_values = init_times_values[1]
    
    initial_investment = GetTotalInvestment(avg_price,quantity)
    if(initial_investment != 0 and initial_investment < init_values[(len(init_values) - 1)]):
        init_color = 'rgb(0, 255, 0)'
    else:
        init_color = 'rgb(255, 0, 0)'

    return render_template("home.html", quantity = quantity, user_access_token = current_user.access_token, init_times = init_times, init_values = init_values, initial_investment = initial_investment, asset_name = asset_name, percentage_of_assets = percentage_of_assets,avg_price = avg_price, current_price = current_price, init_color = init_color)

@app.route("/friends/remove/<username>", methods = ['GET','POST'])
def Remove(username):
    print("removing "+ username)
    Friends1 = Friends.query.filter_by(id = current_user.id, FriendsID = User.query.filter_by(username = username).first().id)
    Friends2 = Friends.query.filter_by(FriendsID = current_user.id, id = User.query.filter_by(username = username).first().id)
    print(Friends1.first(),Friends2.first())
    if Friends1.first() == None:
        Friends2.delete()
    else:
        Friends1.delete()
    db.session.commit()
    return redirect(url_for('friends'))

@app.route("/friends", methods = ['GET','POST'])
def friends():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    # return "Hello!"
    if(request.method == "POST"):
        form = SearchForm()
        print(form.search.data)
        Search = User.query.filter_by(username = form.search.data).first()
        if Search == [] or Search == None or current_user.id == Search.id:
            if Search == [] or Search == None:
                flash('User Does not Exist')
            else:
                flash('You Cannot Add Yourself')
        else:
            namesAlreadyAdding = [person.username2 for person in GetYourRequestedFriends()]
            namesAlreadyAddingYou = [person.username1 for person in GetPeopleRequestingToFriend()]

            AlreadyAdded = [person[0] for person in GetFriends()]
            if Search.username in namesAlreadyAdding or Search.username in AlreadyAdded or Search.username in namesAlreadyAddingYou:
                flash('User Already Has Been Sent a Request or Is Already Added')
            else:
                RequestForF = FriendRequest(id1 =current_user.id,id2 = Search.id,username1 = current_user.username, username2 = Search.username)
                db.session.add(RequestForF)
                db.session.commit()
    RequestingToFriend =  GetPeopleRequestingToFriend()
    PendingAccept = GetYourRequestedFriends()
    Friends = GetFriends()
    
    return render_template("friends.html",RequestingToFriend = RequestingToFriend,PendingAccept=PendingAccept,Friends = Friends)    
    
@app.route("/friends/accept/<FriendId>",methods=["POST",])
def AddFriend(FriendId):
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    if int(FriendId) in [Friend.id1 for Friend in GetPeopleRequestingToFriend()]:
        #add friendship to db
        Friendship = Friends(id =current_user.id,username = current_user.username,FriendsID = FriendId ,FriendsSince = datetime.now() )
        db.session.add(Friendship)
        FriendRequest.query.filter_by(id2 = current_user.id,id1 =FriendId).delete()
        db.session.commit()
        flash("Friend Has Been added")
    else:
        flash("User Has Not Sent you A Request to be Friends")
    return redirect(url_for('friends'))

@app.route("/friends/deny/<FriendId>",methods=["POST",])
def DenyFriend(FriendId):
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    if int(FriendId) in [Friend.id1 for Friend in GetPeopleRequestingToFriend()]:
        FriendRequest.query.filter_by(id2 = current_user.id,id1 =FriendId).delete()
        db.session.commit()
        flash("Friend Has Been denyed")
    else:
        flash("User Has Not Sent you A Request to be Friends")
    return redirect(url_for('friends'))

@app.route("/Positions")
def Positions():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    RefreshT()
    Orders = []
    feed = []
    if current_user.access_token != "":
        try:
            Positions = [Position  for Position in GetAccountData()[0]['securitiesAccount']['positions'] if  Position['instrument'] and  Position['instrument']['symbol'] != "MMDA1"] #gets all non cash positions
            Orders = GetOrders()
            Stocks = [Position['instrument']['symbol']  for Position in Positions]
            feed = getFeedMultiStock([Stocks[0]])
        except KeyError:
            Positions = []
            pass
    else:
        Positions = []
    accountConnected=current_user.access_token!=""
    return render_template('Positions.html',Positions=Positions,Orders=Orders,feed=feed[:8],accountConnected=accountConnected)


@app.route("/cancel/<AccountId>/<OrderID>")
def Cancel(AccountId,OrderID):
    if int(AccountId) in [int(order[0]) for order in GetOrders()] :
        CancelOrder(AccountId,OrderID,current_user)
    else:
        print(AccountId + "is not yours")
        print( [order[0] for order in GetOrders()])
    return redirect(url_for('Positions'))

@app.route("/threshhold/<StockName>")
def Limits(StockName):
    Quanitiy = request.args.get('Quanitiy')
    Top = request.args.get('Top')
    Bot = request.args.get('Bot')
    print("To Set Threshhold")
    print(Quanitiy,StockName,Top,Bot)
    AddThreshholds(Top,Bot,StockName,Quanitiy)
    return redirect(url_for("Positions"))

@app.route("/Market", methods = ['GET','POST'])
def Market():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    form = SearchForm()
    # Have Quick Lookup, Company Search, News
    #if Quick Search
    if form.is_submitted():
        data = GetQuoteNoAcc(form.search.data.upper())
        print(data)
        if data == None or 'Error Message' in data.keys() or (data and data.get("Note",None) != None and len(data['Global Quote']) ==0) or data =={} or data['Global Quote'] == {}:
            flash("No Data Avaiable For That Stock")
            return render_template('Market.html', ticker_dict={},TDdata={},Accountdata = {},feed = GetNews("AAPL"))
        feed = GetNews(form.search.data.upper())
        
        if current_user.access_token !="":
            RefreshTid(current_user.id)
            TDdata = GetTdData(form.search.data.upper(),current_user.access_token)
            Accountdata = GetAccountData()
            Balance = Accountdata[0]['securitiesAccount']['projectedBalances']['cashAvailableForTrading']
            print(TDdata)
            if TDdata == {}:
                flash("Stock Has been Deleted")
                return render_template('Market.html', ticker_dict=None,TDdata={},Accountdata = {})
            Price = TDdata[form.search.data.upper()]["bidPrice"]
        else:
            TDdata = None
            Balance = "Connect Account First"
            if  data !=  {}:
                Price = data['Global Quote']['05. price']
            else:
                Price = 'Cant Retrive That ATM'
        
        #Put data into a dictionary
        ticker_dict = FormatDataToTickerDict(data)

        return render_template('Market.html', TDdata=TDdata,user_access_token = current_user.access_token,ticker_dict=ticker_dict,Price=Price,Balance=Balance, feed=feed)
        # return render_template('Market.html', ticker_dict=ticker_dict,Price=Price,Balance=Balance )
    return render_template('Market.html', ticker_dict=None,TDdata={},Accountdata = {})


@app.route("/Favorites", methods = ['GET','POST'])
def Favorites():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    
    all_ticker_dicts = []
    all_ticker = []
    cur_user = User.query.filter_by(id = current_user.id).first()

    # getting existing favorite stock list rom db
    for fav in FavoriteStocks.query.filter_by(user_id=cur_user.id):
       if fav.Symbol in all_ticker:
           continue       

       if fav.Symbol != "":
           data = GetQuoteNoAcc(fav.Symbol)
           ticker_dict = FormatDataToTickerDict(data)
       if (ticker_dict != {}):
            all_ticker_dicts.append(ticker_dict)
       else:
            all_ticker_dicts = ticker_dict
       all_ticker.append(fav.Symbol)

    # adding new symbol to favorite stocks list 
    form = SearchForm()
    # Search Symbol
    if form.is_submitted():
        if (form.search.data.upper() in all_ticker):
           return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts)
        if (form.search.data.upper() == ""):
           return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts)
           
        qsymbol = FavoriteStocks.query.filter_by(Symbol=form.search.data.upper())
        data = GetQuoteNoAcc(form.search.data.upper())
    
        if data == None or 'Error Message' in data.keys() or (data and data.get("Note",None) != None and len(data['Global Quote']) ==0) or data =={} or data['Global Quote'] == {}:
           return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts)
        
        headers = CaseInsensitiveDict()
        RefreshTid(current_user.id)
        TDdata = GetTdData(form.search.data.upper(),current_user.access_token)
        
        if current_user.access_token !="":
            if TDdata.get(form.search.data.upper(),None)!= None:
                Price = TDdata[form.search.data.upper()]["bidPrice"]
            else:
                flash("Stock Doesnt Exist")
                return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts,TDdata={})

        else:
            if data != None and data.get('Error Message',None) == None and data['Global Quote'] != {}:
                Price = TDdata.get(form.search.data.upper(),{"bidPrice":data['Global Quote']['05. price']})["bidPrice"]
            else:
                flash("Stock Doesnt Exist")
                return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts,TDdata={})
        


        # Put data into a dictionary
        ticker_dict = FormatDataToTickerDict(data)

        if (ticker_dict != {}):
            fav_obj = FavoriteStocks(Symbol=form.search.data.upper(), user_id=cur_user.id) 
            db.session.add(fav_obj)
            db.session.commit()
            all_ticker_dicts.append(ticker_dict)
            all_ticker.append(fav_obj.Symbol)

        return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts,Price=Price)
    return render_template('Favorites.html', all_ticker_dicts=all_ticker_dicts,TDdata={})


@app.route("/About")
def About():
    return render_template('About.html')

@app.route("/Profile")
def Profile():
    code = request.args.get('code')
    if code and not current_user.is_anonymous:
        tokens = GetTokens(code)
        UserToUpdate = User.query.filter_by(email=current_user.email).first()
        UserToUpdate.code = code
        UserToUpdate.access_token = tokens['access_token']
        UserToUpdate.refresh_token = tokens['refresh_token']
        db.session.commit()
        code = None
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    NumFriends = len(GetFriends())
    return render_template('Profile.html',accountConnected=(current_user.access_token!=""),NumFriends=NumFriends)

@app.route("/Profile_Editor", methods=['GET', 'POST'])
def Profile_Editor():
    form = EditProfileForm() 
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        current_user.favorite_stocks = form.favorite_stocks.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('Profile_Editor'))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.favorite_stocks.data = current_user.favorite_stocks
    return render_template('Profile_Editor.html', title = 'Profile Editor', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            print("redirecting Home")
            return redirect(url_for('home'))
        flash('Invalid email address or Password.')    
    return render_template('Login.html', form=form)

@app.route('/register', methods = ['POST','GET'])
def register():
    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            user2 = User(username =form.username.data, email = form.email.data)
            user2.set_password(form.password1.data)
            db.session.add(user2)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('registration.html', form=form)
    except:
        flash('Email Address Is Already In use')  
        return render_template('registration.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

if __name__== "__main__":
    app.run(ssl_context='adhoc')
    

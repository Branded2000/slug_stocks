from flask_login import current_user
from datetime import datetime
from datetime import datetime
from initializers import db
from User import User

class Friends(db.Model):
  friendRow = db.Column(db.Integer, primary_key=True)
  id = db.Column(db.Integer)
  username = db.Column(db.String(50), index=True)
  FriendsID = db.Column(db.Integer, nullable=True)
  FriendsSince = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
  
class FriendRequest(db.Model):
  friendRow = db.Column(db.Integer, primary_key=True)
  id1 = db.Column(db.Integer)
  id2 = db.Column(db.Integer)
  username1 = db.Column(db.String(50), index=True)
  username2 = db.Column(db.String(50), index=True)
  
def GetPeopleRequestingToFriend():
    PeopleRequestingToFriend = FriendRequest.query.filter_by(username2=current_user.username).all()
    return PeopleRequestingToFriend

def GetYourRequestedFriends():
    YourRequestedFriends = FriendRequest.query.filter_by(username1=current_user.username).all()
    return YourRequestedFriends

def AdjustStringTime(Time):
    index = str(Time).find(":")
    return str(Time)[:index-3]

def GetFriends():
    Friends1 = Friends.query.filter_by(id = current_user.id).all()
    Friends2 = Friends.query.filter_by(FriendsID = current_user.id).all()
    FriendIds1= [[User.query.get(friend.FriendsID).username,AdjustStringTime(friend.FriendsSince)]  for friend in Friends1]
    FriendIds2= [[User.query.get(friend.id).username,AdjustStringTime(friend.FriendsSince)] for friend in Friends2]
    AllFriends =  FriendIds1 + FriendIds2
    return AllFriends
from flask_login import current_user
from forms import *
from Auth import *
from User import User
from initializers import db

def RefreshT():
    if current_user.access_token =="":
        return
    UserToUpdate = User.query.filter_by(email=current_user.email).first()
    tokens = GetNewAuthToken(UserToUpdate.refresh_token)
    UserToUpdate.access_token = tokens['access_token']
    db.session.commit()
    
def RefreshTid(id):
    UserToUpdate = User.query.filter_by(id=id).first()
    if UserToUpdate.access_token =="":
        return
    tokens = GetNewAuthToken(UserToUpdate.refresh_token)
    UserToUpdate.access_token = tokens['access_token']
    db.session.commit()
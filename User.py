from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from initializers import db
from sqlalchemy.orm import relationship, backref 
from Favorites import FavoriteStocks 

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique = True, index = True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
  code = db.Column(db.String(1000),default = "")
  access_token =  db.Column(db.String(1000),default="")
  refresh_token =  db.Column(db.String(1000),default="")
  about_me = db.Column(db.String(500))
  favorite_stocks = db.Column(db.String(200))
  fav_stocks = db.relationship('FavoriteStocks', backref='user') # needed for implementation of favorite stocks 
  
  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

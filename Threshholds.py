from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from initializers import db


class Threshholds(UserMixin, db.Model):
      index = db.Column(db.Integer, primary_key=True,index = True, autoincrement=True)
      id = db.Column(db.Integer)
      symbol = db.Column(db.String(10))
      Quantity = db.Column(db.Integer)
      TopThresh = db.Column(db.Float)
      BotThresh = db.Column(db.Float)
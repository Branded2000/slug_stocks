from initializers import db
from sqlalchemy.orm import relationship 
from sqlalchemy import ForeignKey


class FavoriteStocks(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    Symbol = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
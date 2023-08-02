from initializers import db

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True)
    About = db.Column(db.String(500))
    Stock1 = db.Column(db.String(5))
    Stock2 = db.Column(db.String(5))
    Stock3 = db.Column(db.String(5))

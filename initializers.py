from flask import Flask
from flask_login import LoginManager
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
from Auth import *
from flask_migrate import Migrate
from flask_avatars import Avatars
from flask import session

SECRET_KEY = "MagicKey"

app = Flask(__name__)
sslify = SSLify(app)
app.config["SECRET_KEY"] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()
    
migrate = Migrate(app, db)
avatars = Avatars(app)
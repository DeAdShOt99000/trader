import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
csrf = CSRFProtect(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SECRET_KEY"] = "random-text"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_view = "login"
migrate = Migrate(app, db)

with open(os.path.join(basedir, "static\\default_image.jpg"), "rb") as di:
    default_image = di.read()

from app import routes, auth
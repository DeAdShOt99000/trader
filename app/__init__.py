import os
from datetime import datetime, timedelta

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

def price_format(text):
    text = str(text)
    integer, decimal = text.split('.')[0], text.split('.')[1] if len(text.split('.')[1]) > 1 else text.split('.')[1] + '0'
    counter = 0
    new_txt = ''
    for x in range(-1, -len(integer)-1, -1):
        if counter >= 3:
            counter = 0
            new_txt = ',' + new_txt
        new_txt = integer[x] + new_txt
        counter+=1
    return f'{new_txt}.{decimal}'

intervals = ["Just now", "Few minutes ago", "An hour ago", "Few hours ago", "Today", "Yesterday"]

def pretty_date(date):
    return date.strftime("%d %b, %Y")

def date_time_format(dateT):
    current_time = datetime.now()
    time_difference = current_time - dateT
    print(dateT, current_time + timedelta(minutes=5))
    print(time_difference)
    if time_difference < timedelta(minutes=1.5):
        return intervals[0]
    elif time_difference < timedelta(minutes=40):
        return intervals[1]
    elif time_difference < timedelta(hours=1.5):
        return intervals[2]
    elif time_difference < timedelta(hours=12):
        return intervals[3]
    elif time_difference < timedelta(days=0.9):
        return intervals[4]
    elif time_difference < timedelta(days=2):
        return intervals[5]
    else:
        return "From a while"
    
app.jinja_env.globals.update(price_format=price_format)
app.jinja_env.globals.update(date_time_format=date_time_format)
    

with open(os.path.join(basedir, "static\\img\\default_image.jpg"), "rb") as di:
    default_image = di.read()

from app import routes, auth
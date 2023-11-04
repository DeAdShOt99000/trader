import os

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from app.cust_formatting import price_format, date_format

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
    
app.jinja_env.globals.update(price_format=price_format)
app.jinja_env.globals.update(date_format=date_format)

with open(os.path.join(basedir, "static\\img\\default_image.jpg"), "rb") as di:
    default_image = di.read()
    
@app.errorhandler(404)
def page_not_found(error):
    print(type(error))
    return render_template('error.html', error=error), 404

@app.errorhandler(500)
def page_not_found(error):
    print(type(error))
    return render_template('error.html', error=error), 500

from app import routes, auth
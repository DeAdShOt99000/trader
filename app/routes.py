from flask import render_template
from flask_login import current_user, login_required
from app import app, login_manager

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.get("/")
def index():
    return render_template("index.html")
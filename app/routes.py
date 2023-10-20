from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app import app, db, login_manager

from app.models import User, Item
from app.forms import Sell

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.get("/")
def index():
    return render_template("index.html")

@app.route("/sell", methods=("GET", "POST"))
@login_required
def sell():
    form = Sell()
    form.location.data = "1"
    
    if form.validate_on_submit():
        print(form.picture.data.filename)
        item = Item(
            title=form.title.data,
            description=form.description.data,
            picture=form.picture.data.read(),
            location=form.location.data,
            price=form.price.data,
            owner=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("index"))
        
    return render_template("sell.html", form=form)
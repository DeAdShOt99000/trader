from io import BytesIO
from datetime import datetime

from flask import render_template, request, redirect, url_for, send_file
from flask_login import current_user, login_required

from app import app, db, login_manager
from app.models import User, Item, Image
from app.forms import Sell

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#--------------#

@app.get("/image/<int:img_id>")
def serve_image(img_id):
    image = Image.query.get(img_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/jpeg')

@app.get("/")
def index():
    items = Item.query.all()
    return render_template("index.html", items=items)

@app.route("/sell", methods=("GET", "POST"))
@login_required
def sell():
    form = Sell()
    form.location.data = "Maadi"
    
    if form.validate_on_submit():
        item = Item(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            price=form.price.data,
            owner=current_user.id,
            created_at=datetime.now()
        )
        
        db.session.add(item)
        db.session.commit()
        
        image = Image(
            item_id=item.id
        )
        
        image_data = form.image.data.read()
        
        if len(image_data):
            image.image = image_data
        
        db.session.add(image)
        db.session.commit()
        return redirect(url_for("index"))
        
    return render_template("sell.html", form=form)

@app.get("/<int:item_id>/")
def single_item(item_id):
    item = Item.query.get(item_id)
    return render_template("single-item.html", item=item)
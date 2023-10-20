from flask import render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user

from sqlalchemy import or_

from app.models import User
from app.forms import SignUp, LogIn
from app import app, bcrypt, db


@app.route("/auth/login", methods=("GET", "POST"))
def login():
    if not current_user.is_authenticated:
        form = LogIn()
        
        if form.validate_on_submit():
            user = User.query.filter(or_(User.username == form.username_email.data, User.email == form.username_email.data)).first()
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for("index"))
                return "Incorrect password"
            return "No matches"
        
        return render_template("auth/login.html", form=form)
    else:
        return redirect(url_for("index"))

@app.route("/auth/signup", methods=("GET", "POST"))
def signup():
    if not current_user.is_authenticated:
        form = SignUp()
        if form.validate_on_submit():
            user = User(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                username=form.username.data,
                email=form.email.data,
                password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
        return render_template("auth/signup.html", form=form)
    else:
        return redirect(url_for("index"))

@app.get("/auth/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
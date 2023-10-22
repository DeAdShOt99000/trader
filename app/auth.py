import json

from flask import render_template, redirect, url_for, flash, request
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
                    
                    if request.args.get("next"):
                        return redirect(request.args.get("next"))
                    
                    return redirect(url_for("index"))
                
                flash("Incorrect password", "")
            else:
                flash("User does not exist", "")
        
        return render_template("auth/login.html", form=form, next=request.args.get("next"))
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
            
            if request.args.get("next"):
                return redirect(request.args.get("next"))
            
            return redirect(url_for("index"))
        
        return render_template("auth/signup.html", form=form, next=request.args.get("next"))
    else:
        return redirect(url_for("index"))

@app.get("/auth/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.post("/auth/signup/check-user-email")
def check_user_email():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    
    value = username if username else email
    
    if username:
        all_entries = [x.username for x in User.query.all()]
    elif email:
        all_entries = [x.email for x in User.query.all()]
    
    if value in all_entries:
        return {'message': False}
    return {'message': True}
        

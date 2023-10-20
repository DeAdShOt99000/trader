from sqlalchemy.sql import func
from flask_login import UserMixin

from . import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    sent_chat = db.relationship('Chat', backref='sent_by_set', lazy=True, foreign_keys='Chat.sent_by')
    received_chat = db.relationship('Chat', backref='received_by_set', lazy=True, foreign_keys='Chat.received_by')
    
    items = db.relationship('Item', backref='item_owner', lazy=True)
    favourites = db.relationship('Favourite', backref='favourite_owner', lazy=True)
        
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    picture = db.Column(db.LargeBinary)
    location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_sold = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sent_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    received_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    sent_at = db.Column(db.DateTime, default=func.now())
    viewed = db.Column(db.Boolean, default=False)
    
class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    
from io import BytesIO

from sqlalchemy.sql import func
from flask_login import UserMixin

from . import db, default_image

# Association Table for self-referential many-to-many relationship
user_contacts = db.Table('user_contacts',
    db.Column('contact_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('contacted_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

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
    contacts = db.relationship('User', secondary=user_contacts,
                               primaryjoin=(user_contacts.c.contact_id == id),
                               secondaryjoin=(user_contacts.c.contacted_id == id),
                               backref=db.backref('contacted_by', lazy='dynamic'),
                               lazy='dynamic')
        
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_sold = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)
    
    images = db.relationship('Image', backref='images_set', lazy=True)
    chats = db.relationship('Chat', backref='chats_set', lazy=True)
    favourites = db.relationship('Favourite', backref='favourite_item', lazy=True)
    
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, default=BytesIO(default_image).read())
    
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sent_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    received_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    sent_at = db.Column(db.DateTime)
    viewed = db.Column(db.Boolean, default=False)
    
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=True, default=None)
    
class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    
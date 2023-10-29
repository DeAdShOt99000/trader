from io import BytesIO
from flask_login import UserMixin
from . import db, default_image

# Association table for self-referential many-to-many relationship.
user_contacts = db.Table('user_contacts',
    db.Column('contact_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('contacted_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table that connects users with items for 'favourite' functionality.
favourite_items = db.Table('favourite_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
)

# User table for storing users.
class User(db.Model, UserMixin):
    # User table columns
    id = db.Column(db.Integer, primary_key=True)  # User ID
    firstname = db.Column(db.String(50), nullable=False)  # First name
    lastname = db.Column(db.String(50), nullable=False)  # Last name
    username = db.Column(db.String(30), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique email
    password = db.Column(db.String(120), nullable=False)  # Password
    profile_color = db.Column(db.String(25), nullable=True, default=None)  # Profile color
    
    # Relationships
    sent_chat = db.relationship('Chat', backref='sent_by_set', lazy=True, foreign_keys='Chat.sent_by')  # Chats sent by this user
    received_chat = db.relationship('Chat', backref='received_by_set', lazy=True, foreign_keys='Chat.received_by')  # Chats received by this user
    items = db.relationship('Item', backref='item_owner', lazy=True)  # Items posted by this user
    contacts = db.relationship('User', secondary=user_contacts,  # Many-to-many relationship for contacts
                               primaryjoin=(user_contacts.c.contact_id == id),
                               secondaryjoin=(user_contacts.c.contacted_id == id),
                               backref=db.backref('contacted_by', lazy='dynamic'),
                               lazy='dynamic')
    favourites = db.relationship('Item', secondary=favourite_items, backref=db.backref('fav_users', lazy='dynamic'))  # Many-to-many relationship for favorite items

# Item table for storing items.
class Item(db.Model):
    # Item table columns
    id = db.Column(db.Integer, primary_key=True)  # Item ID
    title = db.Column(db.String(100), nullable=False)  # Item title
    description = db.Column(db.Text, nullable=False)  # Item description
    location = db.Column(db.String(100), nullable=False)  # Item location
    price = db.Column(db.Float, default=0, nullable=False)  # Item price
    is_sold = db.Column(db.Boolean, default=False)  # Is item sold?
    created_at = db.Column(db.DateTime)  # Item creation timestamp
    
    # Relationships
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Owner of the item
    images = db.relationship('Image', backref='images_set', lazy=True)  # Images associated with the item
    chats = db.relationship('Chat', backref='chats_set', lazy=True)  # Chats related to the item

# Image table for storing items images.
class Image(db.Model):
    # Image table columns
    id = db.Column(db.Integer, primary_key=True)  # Image ID
    image = db.Column(db.LargeBinary, default=BytesIO(default_image).read())  # Item image in binary format
    
    # Relationships
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)  # Item associated with the image

# Chat table for storing chats.
class Chat(db.Model):
    # Chat table columns
    id = db.Column(db.Integer, primary_key=True)  # Chat ID
    text = db.Column(db.Text)  # Chat message text
    sent_at = db.Column(db.DateTime)  # Timestamp when the chat was sent
    viewed = db.Column(db.Boolean, default=False)  # Has the chat been viewed?
    
    # Relationships
    sent_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # User who sent the chat
    received_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # User who received the chat
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=True, default=None)  # Item related to the chat (optional)

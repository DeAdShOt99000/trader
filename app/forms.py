from string import punctuation, ascii_lowercase, ascii_uppercase, digits

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, FileField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, NumberRange

from app.models import User

required_chars = {"upper": ascii_uppercase, "lower": ascii_lowercase, "digits": digits, "symbols": punctuation}

def validate_password_chars(form, field):
    is_four = 0
    for rule in required_chars:
        for char in required_chars[rule]:
            if char in field.data:
                is_four += 1
                break
    
    if is_four < 4:
        raise ValidationError("Password does not meet requirements")
    
def validate_username(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user:
        raise ValidationError("Username already exists")

def validate_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError("Email already exists")
        
def validate_extension(form, field):
    allowed_extensions = ["png", "jpg", "jpeg", "gif"]
    
    if field.data.filename:
        ext = field.data.filename.split(".")[1]
        if ext not in allowed_extensions:
            raise ValidationError("File type not allowed")
    
class SignUp(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired(), Length(min=1, max=50, message="Name must be between 1 and 50 characters long")])
    lastname = StringField("Last name", validators=[DataRequired(), Length(min=1, max=50, message="Name must be between 1 and 50 characters long")])
    username = StringField("Username", validators=[DataRequired(), validate_username, Length(min=2, max=30, message="Username must be between 2 and 30 characters long")])
    email = EmailField("Email", validators=[DataRequired(), validate_email, Email("Not a valid email")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long"), validate_password_chars])
    r_password = PasswordField("Re-enter password", validators=[DataRequired(), EqualTo("password", message="Password does not match")])
    submit = SubmitField()
    
class LogIn(FlaskForm):
    username_email = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField()
    
class Sell(FlaskForm):
    image = FileField("Upload image", validators=[validate_extension])
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = SelectField("Location", choices=[("Maadi", "Maadi"), ("6 October", "6 October"), ("Haram", "Haram"), ("Faisal", "Faisal"), ("Madenti", "Madenti")])
    price = DecimalField("Price", validators=[NumberRange(min=0, message="The minimum price is 0 EGP")])
    submit = SubmitField()
    
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, FileField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange

from app.my_functions import validate_password_chars, validate_username, validate_email, validate_extension


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
    title = StringField("Title", render_kw={"placeholder": "Item title..."}, validators=[DataRequired()])
    description = TextAreaField("Description", render_kw={"placeholder": "Item description...", "rows": "6"}, validators=[DataRequired()])
    location = SelectField("Location", choices=[("Maadi", "Maadi"), ("6 October", "6 October"), ("Haram", "Haram"), ("Faisal", "Faisal"), ("Madenti", "Madenti")], default="Maadi")
    price = DecimalField("Price", render_kw={"placeholder": "Item price..."}, validators=[NumberRange(min=0, message="The minimum price is 0 EGP")])
    submit = SubmitField()
    
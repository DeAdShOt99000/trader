from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, FileField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange

# Import custom validation functions from your app
from app.cust_validation_funcs import validate_password_chars, validate_username, validate_email, validate_extension

# Form for user registration
class SignUp(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired(), Length(min=1, max=50, message="Name must be between 1 and 50 characters long")])
    lastname = StringField("Last name", validators=[DataRequired(), Length(min=1, max=50, message="Name must be between 1 and 50 characters long")])
    username = StringField("Username", validators=[DataRequired(), validate_username, Length(min=2, max=30, message="Username must be between 2 and 30 characters long")])
    email = EmailField("Email", validators=[DataRequired(), validate_email, Email("Not a valid email")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long"), validate_password_chars])
    r_password = PasswordField("Re-enter password", validators=[DataRequired(), EqualTo("password", message="Password does not match")])
    submit = SubmitField()

# Form for user login
class LogIn(FlaskForm):
    username_email = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField()

# Form for selling or editing an item
class SellEdit(FlaskForm):
    image = FileField("Upload image", validators=[validate_extension])  # File upload field for item image
    title = StringField("Title", render_kw={"placeholder": "Item title..."}, validators=[DataRequired()])  # Item title input field
    description = TextAreaField("Description", render_kw={"placeholder": "Item description...", "rows": "6"}, validators=[DataRequired()])  # Item description input field
    location = SelectField("Location", choices=[("Maadi", "Maadi"), ("6 October", "6 October"), ("Haram", "Haram"), ("Faisal", "Faisal"), ("Madenti", "Madenti")], default="Maadi")  # Dropdown menu for item location
    price = DecimalField("Price", render_kw={"placeholder": "Item price..."}, validators=[NumberRange(min=0, message="The minimum price is 0 EGP")])  # Decimal input field for item price
    submit = SubmitField()  # Submit button for the form

from string import punctuation, ascii_lowercase, ascii_uppercase, digits
from datetime import datetime, timedelta

from wtforms.validators import ValidationError
from app.models import User


# Validation functions for forms.py

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
        
# Datetime formatting function for routes.py

def formatted_dt(date_time: datetime):
    no_zero_hour = date_time.strftime("%I") if date_time.strftime("%I")[0] != '0' else date_time.strftime("%I")[1]
    formatted_time = date_time.strftime(f"{no_zero_hour}:%M %p")
    if date_time.date() == datetime.today().date():
        return ("Today", formatted_time)
    elif date_time.date() == (datetime.today().date() - timedelta(days=1)):
        return ("Yesterday", formatted_time)
    else:
        return (date_time.strftime("%b %d, %Y"), formatted_time)
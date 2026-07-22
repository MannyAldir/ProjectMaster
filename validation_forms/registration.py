from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired,  Length, EqualTo, Email

def strip_whitespace(value:str | None)->str | None:
    if value:
        return value.strip()
    return value

class RegistrationForm(FlaskForm):
    first_name = StringField(
        'First Name',
        validators= [ 
            DataRequired(), 
            Length(max=25)
        ],
        filters=[strip_whitespace]
    )

    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            Length(max=25)
        ],
        filters=[strip_whitespace]
    )

    email = EmailField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Invalid email address'),
            Length(min=6, max=120)
        ],
        filters=[strip_whitespace]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, max=35)
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')

        ]
    )
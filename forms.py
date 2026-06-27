from wtforms import StringField, EmailField, PasswordField, validators
from wtforms.validators import EqualTo, DataRequired, Email
from flask_wtf import FlaskForm
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', filters=[lambda val:val.strip().lower() if val else None],
                             validators=[validators.Length(min=1,max=50), DataRequired('First Name Required')])
    
    last_name = StringField('Last Name', validators=[validators.Length(min=1,max=50), DataRequired('Last Name Required')])
    
    email = EmailField('Email Address',filters= [lambda val:val.strip().lower() if val else None],
                        validators= [validators.Length(min=6,max=50), Email("Enter a valid email address"), 
                        DataRequired('Email Required')])
    password = PasswordField('Password',filters=[lambda val: val.strip() if val else None],
                              validators=[validators.Length(min=8, max=50), DataRequired("Password Required")]
    )
    confirm_password = PasswordField(
        'Confirm Password', [validators.Length(min=8, max=50),
                             DataRequired("Password Required"),
                             EqualTo('password',"Passwords must match")
                             ]
        )

class LoginForm(FlaskForm):
    email = EmailField(
        validators=[
            DataRequired('Email Required'),
            Email(granular_message=True)
        ],
        filters=[lambda x:x.strip().lower() if x else None]
    )
    password = PasswordField(
        label= 'Password',
        validators=[
            DataRequired('Password Required')
        ]
    )

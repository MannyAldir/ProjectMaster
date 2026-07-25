from wtforms import EmailField, PasswordField, ValidationError
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from sqlalchemy import select
from models import User, db

def standarize_email(email: str):
    if email:
        return email.strip().lower()


class loginForm(FlaskForm):
    email = EmailField(
        label= 'Email',
        validators=[DataRequired(message='Email cannot be blank')],
        filters=[standarize_email]
    )

    password = PasswordField(
        label='Password',
        validators=[DataRequired('Invalid email or password')]
    )

    def validate_password(form, field):
        
        stmt = (
            select(User)
            .where(User.email == form.email.data)
        )
        user = db.session.scalar(stmt)

        if not user or not check_password_hash(user.passwordHash, field.data):
            raise ValidationError('Invalid email or password')
        form.user = user
        

        
        



from wtforms import EmailField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from sqlalchemy import select
from models import User, db


class loginForm(FlaskForm):
    email = EmailField(
        label= 'Email',
        validators=[DataRequired(message='Email cannot be blank')],
        filters=[str.strip, str.lower]
    )

    password = PasswordField(
        label='Password',
        validators=[DataRequired('Invalid email or password')]
    )

    def validate_password(self, field):
        
        stmt = (
            select(User)
            .where(User.email == self.email.data)
        )
        user = db.session.scalar(stmt)

        if not user or not check_password_hash(user.passwordHash, self.password.data):
            raise ValidationError('Invalid email or password')
        self.user = user
        

        
        



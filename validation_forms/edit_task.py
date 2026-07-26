from wtforms import ValidationError, TextAreaField, StringField, DateField, SelectField
from wtforms.validators import Length, DataRequired
from flask_wtf import FlaskForm
from datetime import date

class TaskForm(FlaskForm):
    name = StringField(
        label= 'Task Name',
        validators=[
            DataRequired(message='Field cannot be left blank.')]
         )
    description = TextAreaField(label='Description')

    status = SelectField(
        label= 'Status',
        validators=[DataRequired('Please select a status.')],
        choices=[('active','Active'), ('inactive', 'Inactive'), ('completed','Completed')]
    )

    due_date = DateField(
        label='Due Date',
        validators=[
            DataRequired('Please select a date.')
        ]
    )

    def validate_due_date(form, field):
        if field.data < date.today():
            raise ValidationError(message='Select a present or future date')
        
        

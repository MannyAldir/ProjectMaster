from flask_wtf.form import _Auto
from wtforms import ValidationError, TextAreaField, StringField, DateField, SelectField
from wtforms.validators import Length, DataRequired
from flask_wtf import FlaskForm
from datetime import date

class TaskForm(FlaskForm):
    def __init__(self, existing_data=None, formdata=_Auto, **kwargs):
        super().__init__(formdata, **kwargs)
        self.existing_data = existing_data

    taskName = StringField(
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

    dueDate = DateField(
        label='Due Date',
        validators=[
            DataRequired('Please select a date.')
        ]
    )

    def validate_dueDate(form, field):
        if field.data < date.today() and form.existing_data is None :
            raise ValidationError(message='Invalid: New deliverables cannot assign dates retroactively')
        
        

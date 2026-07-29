from flask_wtf.form import _Auto
from wtforms import ValidationError, TextAreaField, StringField, DateField, SelectField
from wtforms.validators import Length, DataRequired, Optional
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
        validators=[Optional()]
    )

    def validate_dueDate(form, field):
        # case the field does not have a date
        if field.data is None:
            return

        # case the task is new then it cannot have a previous date
        if form.existing_data is None and field.data < date.today():
            raise ValidationError("You cannot have a past date for a new task")

        # Case allow an existing task to have no date
        if form.existing_data and field.data == form.existing_data.dueDate:
            return

        # case existing tasks cannot modify their dates to the past
        if form.existing_data and field.data < date.today():
            raise ValidationError("You cannot change your due date to the past unless it was previously empty")

        
        
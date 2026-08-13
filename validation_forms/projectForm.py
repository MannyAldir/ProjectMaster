from datetime import date

from flask_wtf.form import _Auto
from wtforms import TextAreaField, StringField, DateField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
from flask_wtf import FlaskForm

class ProjectForm(FlaskForm):
    def __init__(self, existing_data=None, formdata=_Auto, **kwargs):
        super().__init__(formdata, **kwargs)
        self.existing_data = existing_data

    projectName = StringField(
        label = 'Project Name',
        validators=[DataRequired(message= 'Please enter a project name.')]
    )

    description = TextAreaField(
        label= 'Description',
        validators=[Optional(strip_whitespace=True)]
    )

    startDate = DateField(
        label= 'Start Date',
        validators=[Optional()]
    )

    status = SelectField(
        label='Status',
        validators=[DataRequired('Select a status from the drop down.')],
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('completed', 'Completed')]
    )

    def validate_startDate(form, field):
        # case: form is brand new then we can't set the start before today
        today = date.today()
        if form.existing_data is None and field.data < today:
            raise ValidationError(message= 'Start date must be from today and onward.')

        # Allow the user to update an already existing project without throwing a validation error
        # It must be the case that an already existing date should be the same as the date when it was created
        if form.existing_data and form.existing_data.createdAt.date() == field.data:
            return

        if form.existing_data and field.data < today:
            raise ValidationError(message='Start date must be from today and onward')
    

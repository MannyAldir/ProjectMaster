from datetime import date

from wtforms import TextAreaField, StringField, DateField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
from flask_wtf import FlaskForm

class ProjectForm(FlaskForm):
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
        validators=[DataRequired('Select a status from the drop down.')]
    )

    def validate_startDate(form, field):
        if field and field.data < date.today():
            raise ValidationError('Start date must be either a present or a future date.')


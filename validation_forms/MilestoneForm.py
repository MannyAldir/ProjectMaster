from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms.fields import StringField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
from datetime import date

class MilestoneForm(FlaskForm):
    def __init__(self, existing_data =None,  formdata=_Auto, **kwargs):
        super().__init__(formdata, **kwargs)
        self.existing_data = existing_data

    milestoneName = StringField(
        label= 'Milestone Name',
        validators=[DataRequired(message= 'Please enter a milestone name.')]

    )
    description = TextAreaField(
        label= 'Description',
        validators=[Optional()]
    )

    startDate = DateField(
        label= 'Start Date',
        validators=[DataRequired(message='Select a start date.')]
    )

    endDate = DateField(
        label= 'End Date',
        validators=[DataRequired(message= 'Select a end date.')]
    )

    status = SelectField(
        label='Status',
        validators=[DataRequired(message='Please select a status.')],
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('completed', 'Completed')]
    )

    def validate_startDate(form, field):
        # A new milestone should not have a start date before the present date
        if form.existing_data is None and field.data < date.today():
            raise ValidationError(message='Select a date from today or after today')
        # An existing milestone can be updated as long as dates are the same as original date
        if form.existing_data and field.data == form.existing_data.startDate:
            return

        if form.existing_data and field.data < date.today():
            raise ValidationError(message='Enter a date from today or after today')



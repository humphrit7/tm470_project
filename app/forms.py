"""
Form for the mountain fear finder application
"""


from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, SelectField
from wtforms.fields.html5 import IntegerRangeField


class UploadForm(FlaskForm):
    """
    Form for mountain fear finder application
    """
    route_file = FileField('Upload gpx Route File', validators=[
        FileAllowed(['gpx'], 'gpx files only')
    ])
    route_choice = SelectField('Select Pre-processed Route')
    fear_level = IntegerRangeField('Adjust Fear Level')
    submit = SubmitField('Calculate Scary Points')

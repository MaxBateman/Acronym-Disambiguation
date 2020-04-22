from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms_validators import AlphaNumeric


class QuerytForm(FlaskForm):
    term = StringField('Term', validators=[DataRequired(), Length(max=10)])

    submit = SubmitField('Enter')
class Email(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enter')

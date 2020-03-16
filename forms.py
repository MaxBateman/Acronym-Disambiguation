from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class QuerytForm(FlaskForm):
    term = StringField('Term', validators=[DataRequired()])

    submit = SubmitField('Post')

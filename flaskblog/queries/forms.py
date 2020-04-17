from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, AlphaNumeric


class QuerytForm(FlaskForm):
    term = StringField('Term', validators=[DataRequired(), AlphaNumeric(), Length(max=10)])

    submit = SubmitField('Enter')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class QuerytForm(FlaskForm):
    term = StringField('Term', validators=[DataRequired(), Length(max=50)])

    submit = SubmitField('Enter')

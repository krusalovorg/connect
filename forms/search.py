from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    ttle = StringField('', validators=[DataRequired()])
    submit_s = SubmitField('Поиск')

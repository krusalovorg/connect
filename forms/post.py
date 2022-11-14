from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')

class RemovePostForm(FlaskForm):
    submit = SubmitField('удалить')
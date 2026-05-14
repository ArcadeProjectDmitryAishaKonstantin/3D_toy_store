from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Optional()])
    price = IntegerField('Цена (руб)', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Количество на складе', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    image = FileField('Изображение товара', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')])
    submit = SubmitField('Сохранить')
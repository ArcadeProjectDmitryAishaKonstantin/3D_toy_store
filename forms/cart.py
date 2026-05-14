from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class AddToCartForm(FlaskForm):
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1, max=99)])
    submit = SubmitField('Добавить в корзину')


class UpdateCartForm(FlaskForm):
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=0, max=99)])
    submit = SubmitField('Обновить')
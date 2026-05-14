from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, NumberRange


class ShopInfoForm(FlaskForm):
    phone = StringField('Телефон', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Адрес магазина', validators=[DataRequired()])
    shop_lat = FloatField('Широта магазина', validators=[Optional(), NumberRange(min=-90, max=90)])
    shop_lon = FloatField('Долгота магазина', validators=[Optional(), NumberRange(min=-180, max=180)])
    delivery_base_price = IntegerField('Базовая цена доставки за км (руб)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Сохранить')
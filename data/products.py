import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    stock = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    category = orm.relationship('Category', back_populates='products')
    cart_items = orm.relationship('Cart', back_populates='product')
    order_items = orm.relationship('Order', back_populates='product')

    def __repr__(self):
        return f'<Product> {self.id} {self.title} {self.price}₽'
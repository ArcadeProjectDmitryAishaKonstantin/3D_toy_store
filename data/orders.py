import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price_at_time = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    delivery_cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    total_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, default='pending')
    delivery_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user = orm.relationship('User', back_populates='orders')
    product = orm.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f'<Order> {self.id} user={self.user_id} total={self.total_price} status={self.status}'
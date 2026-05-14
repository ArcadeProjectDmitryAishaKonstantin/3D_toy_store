import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Cart(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cart'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)

    user = orm.relationship('User', back_populates='cart_items')
    product = orm.relationship('Product', back_populates='cart_items')

    def __repr__(self):
        return f'<Cart> user={self.user_id} product={self.product_id} qty={self.quantity}'
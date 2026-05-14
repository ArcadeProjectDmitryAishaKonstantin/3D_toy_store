import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class ShopInfo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'shop_info'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    shop_lat = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    shop_lon = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    delivery_base_price = sqlalchemy.Column(sqlalchemy.Integer, default=50)

    def __repr__(self):
        return f'<ShopInfo> phone={self.phone} email={self.email}'
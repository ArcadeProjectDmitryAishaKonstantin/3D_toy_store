from flask import jsonify
from flask_restful import Resource, reqparse, abort
from flask_login import login_required, current_user
from data import db_session
from data.cart import Cart
from data.products import Product

cart_parser = reqparse.RequestParser()
cart_parser.add_argument('product_id', required=True, type=int)
cart_parser.add_argument('quantity', required=True, type=int)

# Корзина
def get_cart():
    session = db_session.create_session()
    items = session.query(Cart).filter(Cart.user_id == current_user.id).all()
    return [{
        'id': item.id,
        'product_id': item.product_id,
        'title': item.product.title,
        'price': item.product.price,
        'quantity': item.quantity,
        'total': item.product.price * item.quantity
    } for item in items]


class CartResource(Resource):
    @login_required
    def get(self):
        return jsonify({'cart': get_cart(), 'user_id': current_user.id})

    @login_required
    def post(self):
        args = cart_parser.parse_args()
        session = db_session.create_session()

        product = session.get(Product, args['product_id'])
        if not product:
            abort(404, message=f"Product {args['product_id']} not found")

        if product.stock < args['quantity']:
            abort(400, message="Not enough stock")

        cart_item = session.query(Cart).filter(
            Cart.user_id == current_user.id,
            Cart.product_id == args['product_id']
        ).first()

        if cart_item:
            cart_item.quantity += args['quantity']
        else:
            cart_item = Cart(
                user_id=current_user.id,
                product_id=args['product_id'],
                quantity=args['quantity']
            )
            session.add(cart_item)

        session.commit()
        return jsonify({'cart': get_cart(), 'success': 'OK'})


class CartItemResource(Resource):
    @login_required
    def delete(self, item_id):
        session = db_session.create_session()
        cart_item = session.query(Cart).filter(
            Cart.id == item_id,
            Cart.user_id == current_user.id
        ).first()

        if not cart_item:
            abort(404, message=f"Cart item {item_id} not found")

        session.delete(cart_item)
        session.commit()
        return jsonify({'cart': get_cart(), 'success': 'OK'})

    @login_required
    def put(self, item_id):
        args = cart_parser.parse_args()
        session = db_session.create_session()

        cart_item = session.query(Cart).filter(
            Cart.id == item_id,
            Cart.user_id == current_user.id
        ).first()

        if not cart_item:
            abort(404, message=f"Cart item {item_id} not found")

        if args['quantity'] <= 0:
            session.delete(cart_item)
        else:
            cart_item.quantity = args['quantity']

        session.commit()
        return jsonify({'cart': get_cart(), 'success': 'OK'})
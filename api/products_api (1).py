from flask import jsonify
from flask_restful import Resource, reqparse, abort
from data import db_session
from data.products import Product
from data.categories import Category

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('description', required=False)
parser.add_argument('price', required=True, type=int)
parser.add_argument('stock', required=True, type=int)
parser.add_argument('category_id', required=True, type=int)
parser.add_argument('image_id', required=False)


def if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.get(Product, product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductResource(Resource):
    def get(self, product_id):
        if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.get(Product, product_id)
        return jsonify({'product': product.to_dict(only=(
            'id', 'title', 'description', 'price', 'stock', 'category_id', 'image_id'
        ))})

    def delete(self, product_id):
        if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.get(Product, product_id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, product_id):
        if_product_not_found(product_id)
        args = parser.parse_args()
        session = db_session.create_session()
        product = session.get(Product, product_id)

        product.title = args['title']
        product.description = args.get('description', '')
        product.price = args['price']
        product.stock = args['stock']
        product.category_id = args['category_id']
        if args.get('image_id'):
            product.image_id = args['image_id']

        session.commit()
        return jsonify({'success': 'OK', 'product': product.to_dict(only=(
            'id', 'title', 'description', 'price', 'stock', 'category_id', 'image_id'
        ))})


class ProductListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify({'products': [item.to_dict(only=(
            'id', 'title', 'price', 'stock', 'category_id'
        )) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        category = session.get(Category, args['category_id'])
        if not category:
            abort(400, message=f"Category {args['category_id']} not found")

        product = Product(
            title=args['title'],
            description=args.get('description', ''),
            price=args['price'],
            stock=args['stock'],
            category_id=args['category_id'],
            image_id=args.get('image_id', '')
        )
        session.add(product)
        session.commit()
        return jsonify({'id': product.id})
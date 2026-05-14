from flask import Blueprint, render_template, request
from data import db_session
from data.products import Product
from data.categories import Category
from forms.cart import AddToCartForm

blueprint = Blueprint('catalog', __name__, template_folder='templates')


@blueprint.route('/')
@blueprint.route('/index')
def index():
    db_sess = db_session.create_session()
    try:
        products = db_sess.query(Product).limit(6).all()
        categories = db_sess.query(Category).all()
        return render_template('index.html', products=products, categories=categories)
    finally:
        db_sess.close()

# Загрузить каталог
@blueprint.route('/catalog')
def catalog():
    db_sess = db_session.create_session()
    try:
        category_id = request.args.get('category', type=int)
        
        query = db_sess.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        products = query.all()
        categories = db_sess.query(Category).all()
        return render_template('catalog.html', products=products, categories=categories, current_category=category_id)
    finally:
        db_sess.close()

# Детали товара
@blueprint.route('/product/<int:product_id>')
def product_detail(product_id):
    db_sess = db_session.create_session()
    try:
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        if not product:
            return render_template('errors/404.html'), 404
        
        category_name = product.category.name if product.category else None
        form = AddToCartForm()
        
        return render_template('product_card.html', product=product, category_name=category_name, form=form)
    finally:
        db_sess.close()
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from functools import wraps
import os
from werkzeug.utils import secure_filename
from data import db_session
from data.products import Product
from data.categories import Category
from data.orders import Order
from data.shop_info import ShopInfo
from forms.product import ProductForm
from forms.shop import ShopInfoForm

blueprint = Blueprint('admin', __name__, template_folder='templates')

# Проверка пользователя на администратора
def adminka(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def save_image(file):
    if not file or not file.filename:
        return None
    
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = str(int(request.start_time)) if hasattr(request, 'start_time') else ''
    filename = f"{name}_{timestamp}{ext}"
    
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    return f'/static/uploads/{filename}'

# Панель управления администратора (Админка)
@blueprint.route('/admin')
@login_required
@adminka
def dashboard():
    db_sess = db_session.create_session()
    try:
        products = db_sess.query(Product).all()
        orders = db_sess.query(Order).order_by(Order.created_date.desc()).limit(10).all()
        shop_info = db_sess.query(ShopInfo).first()
        return render_template('admin/dashboard.html', products=products, orders=orders, shop_info=shop_info)
    finally:
        db_sess.close()

# Добавить товар
@blueprint.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@adminka
def add_tovar():
    form = ProductForm()
    db_sess = db_session.create_session()
    try:
        categories = db_sess.query(Category).all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
        
        if form.validate_on_submit():
            product = Product(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data,
                category_id=form.category_id.data
            )
            
            if form.image.data:
                image_path = save_image(form.image.data)
                if image_path:
                    product.image_path = image_path
            
            db_sess.add(product)
            db_sess.commit()
            flash('Товар добавлен', 'success')
            return redirect(url_for('admin.dashboard'))
    finally:
        db_sess.close()
    
    return render_template('admin/add_product.html', form=form)

# Редактировать товар
@blueprint.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@adminka
def edit_tovar(product_id):
    db_sess = db_session.create_session()
    try:
        product = db_sess.query(Product).get(product_id)
        
        if not product:
            flash('Товар не найден', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        form = ProductForm()
        categories = db_sess.query(Category).all()
        form.category_id.choices = [(c.id, c.name) for c in categories]
        
        if form.validate_on_submit():
            product.title = form.title.data
            product.description = form.description.data
            product.price = form.price.data
            product.stock = form.stock.data
            product.category_id = form.category_id.data
            
            if form.image.data:
                image_path = save_image(form.image.data)
                if image_path:
                    if product.image_path and product.image_path.startswith('/static/uploads/'):
                        old_file = os.path.join(current_app.root_path, product.image_path.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    product.image_path = image_path
            
            db_sess.commit()
            flash('Товар обновлён', 'success')
            return redirect(url_for('admin.dashboard'))
        
        if request.method == 'GET':
            form.title.data = product.title
            form.description.data = product.description
            form.price.data = product.price
            form.stock.data = product.stock
            form.category_id.data = product.category_id
    finally:
        db_sess.close()
    
    return render_template('admin/edit_product.html', form=form, product=product)

# Удалить товар
@blueprint.route('/admin/delete_product/<int:product_id>')
@login_required
@adminka
def delete_tovar(product_id):
    db_sess = db_session.create_session()
    try:
        product = db_sess.query(Product).get(product_id)
        
        if product:
            if product.image_path and product.image_path.startswith('/static/uploads/'):
                file_path = os.path.join(current_app.root_path, product.image_path.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            db_sess.delete(product)
            db_sess.commit()
            flash('Товар удалён', 'success')
    finally:
        db_sess.close()
    
    return redirect(url_for('admin.dashboard'))

# Изменить информацию магазина
@blueprint.route('/admin/edit_shop_info', methods=['GET', 'POST'])
@login_required
@adminka
def edit_shop_info():
    form = ShopInfoForm()
    db_sess = db_session.create_session()
    try:
        shop_info = db_sess.query(ShopInfo).first()
        
        if not shop_info:
            shop_info = ShopInfo(id=1)
            db_sess.add(shop_info)
            db_sess.commit()
        
        if form.validate_on_submit():
            shop_info.phone = form.phone.data
            shop_info.email = form.email.data
            shop_info.address = form.address.data
            shop_info.shop_lat = form.shop_lat.data
            shop_info.shop_lon = form.shop_lon.data
            shop_info.delivery_base_price = form.delivery_base_price.data
            db_sess.commit()
            flash('Информация о магазине обновлена', 'success')
            return redirect(url_for('admin.dashboard'))
        
        if request.method == 'GET':
            form.phone.data = shop_info.phone
            form.email.data = shop_info.email
            form.address.data = shop_info.address
            form.shop_lat.data = shop_info.shop_lat
            form.shop_lon.data = shop_info.shop_lon
            form.delivery_base_price.data = shop_info.delivery_base_price
    finally:
        db_sess.close()
    
    return render_template('admin/edit_shop_info.html', form=form)

# Заказы администратора
@blueprint.route('/admin/orders')
@login_required
@adminka
def admin_orders():
    db_sess = db_session.create_session()
    try:
        orders = db_sess.query(Order).order_by(Order.created_date.desc()).all()
        return render_template('admin/orders_list.html', orders=orders)
    finally:
        db_sess.close()

# Обновить статус заказа
@blueprint.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
@adminka
def update_order_status(order_id):
    db_sess = db_session.create_session()
    try:
        zakaz = db_sess.query(Order).get(order_id)
        
        if zakaz:
            new_status = request.form.get('status')
            if new_status in ['pending', 'shipped', 'delivered', 'cancelled']:
                zakaz.status = new_status
                db_sess.commit()
                flash(f'Статус заказа #{order_id} изменён на "{new_status}"', 'success')
    finally:
        db_sess.close()
    
    return redirect(url_for('admin.admin_orders'))

# Удалить заказ
@blueprint.route('/admin/orders/<int:order_id>/delete')
@login_required
@adminka
def delete_zakaz(order_id):
    db_sess = db_session.create_session()
    try:
        zakaz = db_sess.query(Order).get(order_id)
        
        if zakaz:
            db_sess.delete(zakaz)
            db_sess.commit()
            flash(f'Заказ #{order_id} удалён', 'success')
    finally:
        db_sess.close()
    
    return redirect(url_for('admin.admin_orders'))

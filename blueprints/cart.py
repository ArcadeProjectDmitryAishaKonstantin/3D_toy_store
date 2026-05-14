from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from data import db_session
from data.cart import Cart
from data.products import Product
from forms.cart import AddToCartForm, UpdateCartForm

blueprint = Blueprint('cart', __name__, template_folder='templates')

# Показать корзину
@blueprint.route('/cart')
@login_required
def view_korzina():
    db_sess = db_session.create_session()
    try:
        cart_items = db_sess.query(Cart).filter(Cart.user_id == current_user.id).all()
        total = sum(item.product.price * item.quantity for item in cart_items if item.product)
        return render_template('cart.html', cart_items=cart_items, total=total)
    finally:
        db_sess.close()

# Добавить товар в корзину
@blueprint.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_korzina(product_id):
    form = AddToCartForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            product = db_sess.query(Product).filter(Product.id == product_id).first()
            if not product:
                flash('Товар не найден', 'danger')
                return redirect(url_for('catalog.catalog'))
            
            quantity = form.quantity.data
            if product.stock < quantity:
                flash(f'Недостаточно товара на складе. Доступно: {product.stock}', 'danger')
                return redirect(url_for('catalog.product_detail', product_id=product_id))
            
            cart_item = db_sess.query(Cart).filter(
                Cart.user_id == current_user.id,
                Cart.product_id == product_id
            ).first()
            
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = Cart(
                    user_id=current_user.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db_sess.add(cart_item)
            
            db_sess.commit()
            flash('Товар добавлен в корзину', 'success')
        except Exception as e:
            db_sess.rollback()
            flash(f'Ошибка при добавлении: {str(e)}', 'danger')
        finally:
            db_sess.close()
    
    return redirect(url_for('catalog.product_detail', product_id=product_id))

# Обновить корзину
@blueprint.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_korzina(item_id):
    quantity = request.form.get('quantity', type=int)
    
    if quantity is None or quantity < 0:
        flash('Некорректное количество', 'danger')
        return redirect(url_for('cart.view_korzina'))
    
    db_sess = db_session.create_session()
    try:
        cart_item = db_sess.query(Cart).filter(
            Cart.id == item_id,
            Cart.user_id == current_user.id
        ).first()
        
        if not cart_item:
            flash('Товар не найден в корзине', 'danger')
            return redirect(url_for('cart.view_cart'))
        
        if quantity == 0:
            db_sess.delete(cart_item)
            flash('Товар удалён из корзины', 'success')
        else:
            product = cart_item.product
            if product.stock < quantity:
                flash(f'Недостаточно товара на складе. Доступно: {product.stock}', 'danger')
                return redirect(url_for('cart.view_cart'))
            cart_item.quantity = quantity
            flash('Корзина обновлена', 'success')
        
        db_sess.commit()
    finally:
        db_sess.close()
    
    return redirect(url_for('cart.view_korzina'))

# Убрать товар из корзины
@blueprint.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_korzina(item_id):
    db_sess = db_session.create_session()
    try:
        cart_item = db_sess.query(Cart).filter(
            Cart.id == item_id,
            Cart.user_id == current_user.id
        ).first()
        
        if cart_item:
            db_sess.delete(cart_item)
            db_sess.commit()
            flash('Товар удалён из корзины', 'success')
    finally:
        db_sess.close()
    
    return redirect(url_for('cart.view_korzina'))
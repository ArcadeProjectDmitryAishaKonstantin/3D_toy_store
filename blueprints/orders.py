from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from data import db_session
from data.cart import Cart
from data.orders import Order
from data.products import Product
from data.shop_info import ShopInfo
from blueprints.delivery import get_coordinates, calculate_distance

blueprint = Blueprint('orders', __name__, template_folder='templates')

# Создать заявку на заказ 3д фигурки
@blueprint.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    db_sess = db_session.create_session()
    try:
        raw_cart_items = db_sess.query(Cart).filter(Cart.user_id == current_user.id).all()

        cart_items = [item for item in raw_cart_items if item.product is not None]

        bad_items = [item for item in raw_cart_items if item.product is None]
        if bad_items:
            for bad in bad_items:
                db_sess.delete(bad)
            db_sess.commit()

        if not cart_items:
            flash('Ваша корзина пуста или товары в ней больше недоступны', 'warning')
            return redirect(url_for('catalog.catalog'))

        if request.method == 'POST':
            city = request.form.get('city', '')
            address = request.form.get('address', '')
            full_address = f"{city}, {address}" if city and address else city or address
            shop_info = db_sess.query(ShopInfo).first()
            delivery_cost = 0

            if shop_info and shop_info.shop_lat and shop_info.shop_lon and full_address:
                address_lat, address_lon = get_coordinates(full_address)
                if address_lat is not None:
                    distance = calculate_distance(
                        address_lat, address_lon,
                        shop_info.shop_lat, shop_info.shop_lon
                    )
                    delivery_cost = int(distance * (shop_info.delivery_base_price or 50))
                else:
                    print(f"Не удалось получить координаты для адреса: {full_address}")

            for item in cart_items:
                # Здесь item.product гарантированно существует благодаря фильтрации выше
                item_total = item.product.price * item.quantity

                order = Order(
                    user_id=current_user.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_time=item.product.price,
                    delivery_cost=delivery_cost,
                    total_price=item_total + delivery_cost,
                    delivery_address=full_address
                )
                db_sess.add(order)

                product = item.product
                product.stock -= item.quantity

                db_sess.delete(item)

            db_sess.commit()
            flash(f'Заказ оформлен! Стоимость доставки: {delivery_cost}₽', 'success')
            return redirect(url_for('orders.order_history'))

        total = sum(item.product.price * item.quantity for item in cart_items)
        return render_template('checkout.html', cart_items=cart_items, total=total)

    except Exception as e:
        print(f"Ошибка при оформлении заказа: {e}")
        db_sess.rollback()
        flash("Произошла ошибка при обработке заказа.", "danger")
        return redirect(url_for('cart.view_korzina'))
    finally:
        db_sess.close()

# История заказов
@blueprint.route('/orders')
@login_required
def order_history():
    db_sess = db_session.create_session()
    try:
        orders = db_sess.query(Order).filter(
            Order.user_id == current_user.id
        ).order_by(Order.created_date.desc()).all()
        return render_template('orders.html', orders=orders)
    finally:
        db_sess.close()

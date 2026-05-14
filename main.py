from flask import Flask, render_template
from flask_login import LoginManager
from flask_restful import Api
from data import db_session
from data.users import User
from data.shop_info import ShopInfo
from data.categories import Category
from blueprints import auth, catalog, cart, orders, admin, delivery
from api.products_api import ProductResource, ProductListResource
from api.cart_api import CartResource, CartItemResource
from api.delivery_api import DeliveryCalculateResource

app = Flask(__name__)
app.config['SECRET_KEY'] = '3d_toy_store_secret_key_2026'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему'

# Загрузить информацию пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.get(User, int(user_id))
    finally:
        db_sess.close()


api = Api(app)
api.add_resource(ProductListResource, '/api/products')
api.add_resource(ProductResource, '/api/products/<int:product_id>')
api.add_resource(CartResource, '/api/cart')
api.add_resource(CartItemResource, '/api/cart/<int:item_id>')
api.add_resource(DeliveryCalculateResource, '/api/delivery/calculate')


app.register_blueprint(auth.blueprint)
app.register_blueprint(catalog.blueprint)
app.register_blueprint(cart.blueprint)
app.register_blueprint(orders.blueprint)
app.register_blueprint(admin.blueprint)
app.register_blueprint(delivery.blueprint)

# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove_session()

# Обновить информацию магазина
def shop_informatsia():
    db_sess = db_session.create_session()
    try:
        if db_sess.query(ShopInfo).count() == 0:
            shop_info = ShopInfo(
                id=1,
                phone='+7 (999) 123-45-67',
                email='shop@3dtoys.ru',
                address='г. Москва, ул. Примерная, д. 1',
                shop_lat=55.751244,
                shop_lon=37.618423,
                delivery_base_price=50
            )
            db_sess.add(shop_info)
            db_sess.commit()
            print("Информация о магазине добавлена")
    finally:
        db_sess.close()

# Обновить категории
def categorii():
    db_sess = db_session.create_session()
    try:
        if db_sess.query(Category).count() == 0:
            kategorii = ['Животные', 'Персонажи из игр', 'Аниме-фигурки', 'Сувениры', 'Хозяйственные принадлежности']
            for kategoria_name in kategorii:
                kategoria = Category(name=kategoria_name)
                db_sess.add(kategoria)
            db_sess.commit()
            print(f"Категории добавлены: {', '.join(kategorii)}")
        else:
            print(f"Категории уже есть: {db_sess.query(Category).count()} шт.")
    finally:
        db_sess.close()

# Добавить админа (в случае если его нет)
def create_admin():
    db_sess = db_session.create_session()
    try:
        admin = db_sess.query(User).filter(User.email == "admin@3dtoys.ru").first()
        
        if not admin:
            admin = User(
                name="Admin",
                email="admin@3dtoys.ru",
                address="г. Москва, Кремль",
                city="Москва",
                is_admin=True
            )
            admin.set_password("admin123")
            db_sess.add(admin)
            db_sess.commit()
            print("=" * 50)
            print("Администратор создан!")
            print("Email: admin@3dtoys.ru")
            print("Пароль: admin123")
            print("=" * 50)
        else:
            print("Администратор уже существует")
    finally:
        db_sess.close()


if __name__ == '__main__':
    db_session.global_init("db/store.db")
    shop_informatsia()
    categorii()
    create_admin()
    app.run(port=8080, host='127.0.0.1', debug=True)
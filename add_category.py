from data import db_session
from data.categories import Category

db_session.global_init("db/store.db")
sess = db_session.create_session()

kategorii = ['Животные', 'Персонажи из игр', 'Аниме-фигурки', 'Сувениры', 'Хозяйственные принадлежности']

for kategoria_name in kategorii:
    kategoria = Category(name=kategoria_name)
    sess.add(kategoria)

sess.commit()
print("Категории добавлены")

for kategoria in sess.query(Category).all():
    print(f"ID: {kategoria.id}, Name: {kategoria.name}")
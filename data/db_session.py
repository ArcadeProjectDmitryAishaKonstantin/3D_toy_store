import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, scoped_session

SqlAlchemyBase = orm.declarative_base()

__factory = None
__scoped_factory = None

# Подключение к базе данных
def global_init(db_file):
    global __factory, __scoped_factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, pool_size=20, max_overflow=40)
    __factory = orm.sessionmaker(bind=engine)
    __scoped_factory = scoped_session(__factory)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __scoped_factory
    return __scoped_factory()


def remove_session():
    if __scoped_factory:
        __scoped_factory.remove()
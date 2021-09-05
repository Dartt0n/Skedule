from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    SmallInteger,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from jproperties import Properties
from typing import Any, List
from os import path
from database.models import User

Base = declarative_base()


class TelegramUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    telegram_id = Column(Integer, nullable=False)
    is_student = Column(Boolean, nullable=False)
    subclass = Column(String(length=15), nullable=True)
    teacher_name = Column(String(length=100), nullable=True)
    status = Column(SmallInteger, nullable=True)
    requests_left = Column(SmallInteger, nullable=True)
    last_payment_datetime = Column(DateTime, nullable=True)
    subscription_until = Column(DateTime, nullable=True)


class TelegramAgent:
    def __init__(self):
        properties = Properties()
        with open(
            path.abspath(path.join(path.dirname(__file__), "..", ".properties")), "rb"
        ) as config:
            properties.load(config)

        def get_config(key: str) -> Any:
            return properties[key].data

        DB_USER_NAME = get_config("DB_TG_USER_NAME")
        DB_DATABASE_NAME = get_config("DB_DATABASE_NAME")
        DB_USER_PASSWORD = get_config("DB_TG_USER_PASSWORD")
        DB_DATABASE_HOST = get_config("DB_DATABASE_HOST")
        self.engine = create_engine(
            f"mariadb+mariadbconnector://{DB_USER_NAME}:{DB_USER_PASSWORD}@{DB_DATABASE_HOST}:3306/{DB_DATABASE_NAME}"
        )
        self.session = sessionmaker(bind=self.engine)()

    def check_if_user_exists(self, telegram_id: int) -> bool:
        user_with_id = (
            self.session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        )
        return user_with_id is not None

    def create_new_user(self, **db_params) -> None:
        telegram_user = TelegramUser(**db_params)
        self.session.add(telegram_user)
        self.session.commit()

    def change_subclass(self, telegram_id: int, subclass: str) -> None:
        # sourcery skip: class-extract-method
        user = (
            self.session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        )
        user.subclass = subclass
        user.is_student = True
        user.teacher_name = None
        self.session.commit()

    def change_teacher_name(self, telegram_id: int, teacher_name: str) -> None:
        teacher = (
            self.session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        )
        teacher.teacher_name = teacher_name
        teacher.is_student = False
        teacher.subclass = None
        self.session.commit()

    def get_user(self, telegram_id: int) -> User:
        return User.from_database(
            self.session.query(TelegramUser).filter_by(telegram_id=telegram_id).first()
        )

    def get_chats(self) -> List[int]:
        return list(map(lambda x: x.telegram_id, self.session.query(TelegramUser).all()))

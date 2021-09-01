from sqlalchemy import create_engine, Column, Integer, SmallInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from jproperties import Properties
from typing import Any
from os import path

# loading config
DIR = path.abspath(".")

with open(path.join(DIR, ".properties"), "rb") as config_file:
    properties = Properties()
    properties.load(config_file)


def get_config(key: str) -> Any:
    return properties[key].data


DB_USER_NAME = "root"
DB_DATABASE_NAME = get_config("DB_DATABASE_NAME")
DB_USER_PASSWORD = get_config("DB_ROOT_PASSWORD")
DB_DATABASE_HOST = get_config("DB_DATABASE_HOST")

# create engine for remote database
mariadb = create_engine(
    f"mariadb+mariadbconnector://{DB_USER_NAME}:{DB_USER_PASSWORD}@{DB_DATABASE_HOST}:3306/{DB_DATABASE_NAME}"
)
print("connected")
Base = declarative_base()


class MDB_Lesson(Base):
    __tablename__ = "tt10_20_21"
    id = Column(Integer, nullable=False, primary_key=True)
    lesson_number = Column(SmallInteger, nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    subject = Column(String(length=100), nullable=False)
    teacher = Column(String(length=100), nullable=True)
    cabinet = Column(String(length=50), nullable=False)
    subclass = Column(String(length=15), nullable=False)


mariadb_session = sessionmaker(bind=mariadb)()

sqlite = create_engine("sqlite:///database/database.db")
Base = declarative_base()


class SLT_Lessons(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    lesson_number = Column(Integer)
    subject = Column(String)
    day_of_week = Column(Integer)
    teacher = Column(String)
    cabinet = Column(String)
    class_group = Column(String)


sqlite_session = sessionmaker(bind=sqlite)()

all_sqlite_data = sqlite_session.query(SLT_Lessons).all()

for sqlite_lesson_row in all_sqlite_data:
    mariadb_lesson_row = MDB_Lesson(
        lesson_number=sqlite_lesson_row.lesson_number,
        day_of_week=sqlite_lesson_row.day_of_week,
        subject=sqlite_lesson_row.subject,
        teacher=sqlite_lesson_row.teacher,
        cabinet=sqlite_lesson_row.cabinet,
        subclass=sqlite_lesson_row.class_group,
    )
    mariadb_session.add(mariadb_lesson_row)
    mariadb_session.commit()

print("done")

from sqlalchemy import create_engine, Column, Integer, SmallInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from jproperties import Properties
from typing import Any
from os import path
import csv


weekdays = {
    "Понедельник": 1,
    "Вторник": 2,
    "Пятница": 5,
    "Среда": 3,
    "Суббота": 6,
    "Четверг": 4,
}
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


class Lesson(Base):
    __tablename__ = "timetable"
    id = Column(Integer, nullable=False, primary_key=True)
    lesson_number = Column(SmallInteger, nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    subject = Column(String(length=100), nullable=False)
    teacher = Column(String(length=100), nullable=True)
    cabinet = Column(String(length=50), nullable=False)
    subclass = Column(String(length=15), nullable=False)


mariadb_session = sessionmaker(bind=mariadb)()


with open("/home/dartt0n/Downloads/blka/timetable 1 korp.csv") as file:
    rows = csv.reader(file, delimiter=",")
    for lessons in rows:
        for lesson in lessons:
            print(lesson)
            weekday, lesson_number, subclass, cabinet, subject, teacher = map(
                lambda x: x.strip(), lesson.split("~")
            )
            weekday = weekdays[weekday]

            print(weekday, lesson_number, subclass, cabinet, subject, teacher)

            l = Lesson(
                lesson_number=lesson_number,
                subclass=subclass,
                day_of_week=weekday,
                subject=subject,
                teacher=teacher,
                cabinet=cabinet,
            )
            mariadb_session.add(l)
            mariadb_session.commit()

from datetime import datetime
from typing import Optional, Union, List
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel
from dataclasses import dataclass
from jproperties import Properties
from os.path import abspath, join, dirname
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Table


@dataclass
class DatabaseRow:
    id: int
    lesson_number: int
    day_of_week: int
    subject: str
    teacher: str
    cabinet: str
    subclass: str


class Teacher(BaseModel):
    name: str


class Student(BaseModel):
    subclass: str


properties = Properties()
with open(abspath(join(dirname(__file__), "..", ".properties")), "rb") as config:
    properties.load(config)


def get_config(key: str) -> str:
    return properties[key].data


DB_USER_NAME = get_config("DB_TG_USER_NAME")
DB_DATABASE_NAME = get_config("DB_DATABASE_NAME")
DB_USER_PASSWORD = get_config("DB_TG_USER_PASSWORD")
DB_DATABASE_HOST = get_config("DB_DATABASE_HOST")

engine = create_engine(
    f"mariadb+mariadbconnector://{DB_USER_NAME}:{DB_USER_PASSWORD}@{DB_DATABASE_HOST}:3306/{DB_DATABASE_NAME}",
    isolation_level="READ UNCOMMITTED",
)
# create database and configure it with engine
base = declarative_base()
base.metadata.reflect(engine)
# create session. `sessionmaker` return class, so we need use `()` to create an object
session: Session = sessionmaker(bind=engine)()

Timetable = base.metadata.tables["timetable"]


app = FastAPI()


def get_filter(user):
    if isinstance(user, Teacher):
        return {"teacher": user.name}
    else:
        return {"subclass": user.subclass}

def get_current_day_of_week() -> int:
    return datetime.today().weekday() + 1

def jsonify(lesson):
    return {
        "lesson_number": lesson.lesson_number,
        "subclass": lesson.subclass,
        "subject": lesson.subject,
        "teacher": lesson.teacher,
        "cabinet": lesson.cabinet,
    }


@app.get("/api/lesson/next")
def get_next_lesson(user: Union[Teacher, Student]):
    pass


@app.get("/api/day/certain/{day_of_week}")
def get_certain_day(user: Union[Teacher, Student], day_of_week: int):
    timetable_filter = get_filter(user)

    daily_timetable: List[DatabaseRow] = (
        session.query(Timetable)
        .filter_by(day_of_week=day_of_week, **timetable_filter)
        .all()
    )
    return {
        day_of_week: [
            jsonify(lesson)
            for lesson in sorted(daily_timetable, key=lambda x: x.lesson_number)
        ]
    }


@app.get("/api/day/tomorrow")
def get_tomorrow(user: Union[Teacher, Student]):
    return get_certain_day(user, get_current_day_of_week()+1)


@app.get("/api/day/today")
def get_today(user: Union[Teacher, Student]):
    return get_certain_day(user, get_current_day_of_week())


@app.get("/api/week")
def get_week(user: Union[Teacher, Student]):
    timetable_filter = get_filter(user)

    all_week_data: List[DatabaseRow] = (
        session.query(Timetable).filter_by(**timetable_filter).all()
    )

    result = {day_of_week: [] for day_of_week in range(1, 7)}

    for lesson in all_week_data:
        result[lesson.day_of_week].append(jsonify(lesson))

    for _, dayly_timetable in result.items():
        dayly_timetable.sort(key=lambda x: x["lesson_number"])

    return result

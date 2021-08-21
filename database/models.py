from typing import List
from dataclasses import dataclass

@dataclass
class DatabaseConnection:
    username: str
    password: str
    host: str
    database_name: str


@dataclass
class TableLesson:
    lesson_number: int
    subject: int
    teacher: str
    cabinet: str


@dataclass
class TableDay:
    lessons: List[TableLesson]
    day_of_week: int

@dataclass
class User:
    parallel: str
    semigroup: str

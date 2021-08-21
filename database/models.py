from typing import List
from dataclasses import dataclass


@dataclass
class DatabaseConnection:
    """
    Dataclass describing connection to database 
    """
    username: str
    password: str
    host: str
    database_name: str


@dataclass
class TableLesson:
    """
    Dataclass describing lesson in table
    """
    lesson_number: int
    subject: int
    teacher: str
    cabinet: str


@dataclass
class TableDay:
    """
    Dataclass describing day with lessons in table
    """
    lessons: List[TableLesson]
    day_of_week: int


@dataclass
class User:
    """
    Dataclass describing user
    """
    parallel: str
    subclass: str

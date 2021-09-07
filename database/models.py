from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseRow:
    id: int
    lesson_number: int
    day_of_week: int
    subject: str
    teacher: str
    cabinet: str
    subclass: str


@dataclass
class TableLesson:
    """
    Dataclass describing lesson in table
    """

    lesson_number: int
    subject: int
    teacher: str
    cabinet: str
    subclass: str

    def from_database(database_row: DatabaseRow):
        return TableLesson(
            database_row.lesson_number,
            database_row.subject,
            database_row.teacher,
            database_row.cabinet,
            database_row.subclass,
        )


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

    table_name: str
    filter: Dict[str, Any]

    def from_database(user):
        if user.is_student:
            return Student(user.subclass)
        return Teacher(user.teacher_name)


class Teacher(User):
    def __init__(self, name: str):
        self.name = name
        super(Teacher, self).__init__("timetable", {"teacher": name})


class Student(User):
    def __init__(self, subclass: str):
        self.subclass = subclass
        super(Student, self).__init__(f"timetable", {"subclass": subclass})

from jproperties import Properties
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Table
from database.models import DatabaseRow, User, TableLesson, TableDay
from typing import List
from jproperties import Properties
from os import path


class Agent:
    def __init__(self) -> None:
        """
        Agent is need to access database, encapsulating sqlalchemy methods
        """

        properties = Properties()
        with open(
            path.abspath(path.join(path.dirname(__file__), "..", ".properties")),
            "rb",
        ) as config:
            properties.load(config)

        def get_config(key: str):
            return properties[key].data

        DB_USER_NAME = get_config("DB_TG_USER_NAME")
        DB_DATABASE_NAME = get_config("DB_DATABASE_NAME")
        DB_USER_PASSWORD = get_config("DB_TG_USER_PASSWORD")
        DB_DATABASE_HOST = get_config("DB_DATABASE_HOST")

        self.__engine = create_engine(
            f"mariadb+mariadbconnector://{DB_USER_NAME}:{DB_USER_PASSWORD}@{DB_DATABASE_HOST}:3306/{DB_DATABASE_NAME}",
            isolation_level="READ UNCOMMITTED",
        )
        # create database and configure it with engine
        self.__base = declarative_base()
        self.__base.metadata.reflect(self.__engine)
        # create session. `sessionmaker` return class, so we need use `()` to create an object
        self.__session: Session = sessionmaker(bind=self.__engine)()
        self.__session.execute("SET SESSION query_cache_type = OFF")

    def __get_table(self, user: User) -> Table:
        """Returns table, which can be received from metadata of database.
        Each user contain variable `table_name` generated in time user registered
        """
        return self.__base.metadata.tables[user.table_name]

    def get_week(self, user: User) -> List[TableDay]:
        """Returns weekly schedule for certain subclass or teacher (defined by `user.filter`)
        `user.filter` generated in time user registered
        """
        all_weekly_data: List[DatabaseRow] = (
            self.__session.query(self.__get_table(user)).filter_by(**user.filter).all()
        )

        # Create array for every day (indexed by 1-6, like Mon-Sat)
        table_days = [TableDay([], i) for i in range(1, 7)]

        for table_row in all_weekly_data:
            # extract and rebase data
            lesson = TableLesson.from_database(table_row)
            # save lessons to certain day
            table_days[table_row.day_of_week - 1].lessons.append(lesson)
        # sort lessons by lesson number
        for day in table_days:
            day.lessons.sort(key=lambda x: x.lesson_number)

        return table_days

    def get_day(self, user: User, day_of_week: int) -> TableDay:
        """Returns daily schedule for certain class or teacher on certain day
        Uses `user.filter` for filtering database output
        """
        all_daily_data: List[DatabaseRow] = (
            self.__session.query(self.__get_table(user))
            .filter_by(
                day_of_week=day_of_week, **user.filter
            )  # filter by subclass or teacher name and day_of_week
            .all()
        )
        # rebase data
        return TableDay(
            day_of_week=day_of_week,
            lessons=sorted(
                [TableLesson.from_database(table_row) for table_row in all_daily_data],
                key=lambda x: x.lesson_number,
            ),
        )

    def get_lesson(
        self, user: User, day_of_week: int, lesson_number: int
    ) -> TableLesson:
        """Returns lesson schedule for certain class or teacher, on certain day in certain lesson"""
        table_row: DatabaseRow = (
            self.__session.query(self.__get_table(user))
            .filter_by(
                day_of_week=day_of_week,
                lesson_number=lesson_number,
                **user.filter,
            )
            .first()
        )
        if not table_row:
            return None
        return TableLesson.from_database(table_row)

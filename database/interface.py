from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Table
from models import DatabaseRow, User, DatabaseConnection, TableLesson, TableDay
from typing import List


class Agent:
    def __init__(self, db_conn: DatabaseConnection) -> None:
        """
        Agent is need to access database, encapsulating sqlalchemy methods
        """
        self.__engine = create_engine(  # connect to remote database server
            f"mariadb+mariadbconnector://{db_conn.username}:{db_conn.password}@{db_conn.host}:3306/{db_conn.database_name}"
        )
        # create database and configure it with engine
        self.__base = declarative_base()
        self.__base.metadata.reflect(self.__engine)
        # create session. `sessionmaker` return class, so we need use `()` to create an object
        self.__session = sessionmaker(bind=self.__engine)()

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
            lessons=[
                TableLesson.from_database(table_row) for table_row in all_daily_data
            ],
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
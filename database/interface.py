from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Table
from database.models import User, DatabaseConnection, TableLesson, TableDay
from typing import List

# Format for table name. Parallel should be passed in format string
TABLE_FORMAT = "tt{}_20_21".format


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
        Table identified with TABLE_FORMAT format string for each parallel (8s, 9s, 10s, 11s)
        """
        return self.__base.metadata.tables[TABLE_FORMAT(user.parallel)]

    def get_week(self, user: User) -> List[TableDay]:
        """Returns weekly schedule for certain class (subclass)"""
        all_weekly_data = (
            self.__session.query(self.__get_table(user))
            .filter_by(
                subclass=user.subclass
            )  # database store only one week, so we need to filter only by subclass
            .all()
        )

        # Create array for every day (indexed by 1-6, like Mon-Sat)
        table_days = [TableDay([], i) for i in range(1, 7)]

        for table_row in all_weekly_data:
            # extract and rebase data
            lesson = TableLesson(
                table_row.lesson_number,
                table_row.subject,
                table_row.teacher,
                table_row.cabinet,
            )
            # save lessons to certain day
            table_days[table_row.day_of_week - 1].lessons.append(lesson)
        # sort lessons by lesson number
        for day in table_days:
            day.lessons.sort(key=lambda x: x.lesson_number)

        return table_days

    def get_day(self, user: User, day_of_week: int) -> TableDay:
        """Returns daily schedule for certain class and day"""
        all_daily_data = (
            self.__session.query(self.__get_table(user))
            .filter_by(
                subclass=user.subclass, day_of_week=day_of_week
            )  # filter by subclass and day_of_week
            .all()
        )
        # rebase data
        return TableDay(
            day_of_week=day_of_week,
            lessons=[
                TableLesson(
                    table_row.lesson_number,
                    table_row.subject,
                    table_row.teacher,
                    table_row.cabinet,
                )
                for table_row in all_daily_data
            ],
        )

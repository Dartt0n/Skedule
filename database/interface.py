from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from database.models import *


TABLE_FORMAT = "tt{}_20_21".format

class Agent:
    def __init__(self, db_conn: DatabaseConnection) -> None:
        self.__engine = create_engine(
            f"mariadb+mariadbconnector://{db_conn.username}:{db_conn.password}@{db_conn.host}:3306/{db_conn.database_name}"
        )
        self.__base = declarative_base()
        self.__base.metadata.reflect(self.__engine)
        self.__session = sessionmaker(bind=self.__engine)()

    def __get_table(self, user):
        return self.__base.metadata.tables[TABLE_FORMAT(user.parallel)]

    def get_week(self, user):
        all_week_data = (
            self.__session.query(self.__get_table(user))
            .filter_by(semigroup=user.semigroup)
            .all()
        )

        table_days = [TableDay([], i) for i in range(1, 7)]
        for table_row in all_week_data:
            lesson = TableLesson(
                table_row.lesson_number,
                table_row.subject,
                table_row.teacher,
                table_row.cabinet,
            )
            table_days[table_row.day_of_week - 1].lessons.append(lesson)
        return table_days

    def get_day(self, user, day_of_week: int):
        all_day_data = (
            self.__session.query(self.__get_table(user))
            .filter_by(semigroup=user.semigroup, day_of_week=day_of_week)
            .all()
        )
        return TableDay(day_of_week=day_of_week, lessons=[
            TableLesson(table_row.lesson_number, table_row.subject, table_row.teacher, table_row.cabinet)
            for table_row in all_day_data
        ])


# --=--

a = Agent(
    DatabaseConnection("telegram_user", "YywQZDSOcAaDl8OisL", "skedule.ru", "skedule")
)

user = User("10", "10е1")
x = a.get_day(user, 1)
print()
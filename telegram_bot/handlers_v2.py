from datetime import datetime
from os import path
from time import sleep
from database.interface import Agent
from database.models import Student
from database.telegram import TelegramAgent
from datetimerange import DateTimeRange
from telegram import Update
from telegram.ext import CallbackContext, Updater

from telegram_bot.enums import CallbackEnum, State
from telegram_bot.support_functions import (
    get_current_day_of_week,
    get_json,
    get_lesson_number,
    get_telegram_id,
    markup_from,
    update_query,
)
from logger_config import logger

LESSON_TIME = {
    1: "9:00 - 9:40",
    2: "9:50 - 10:30",
    3: "10:45 - 11:25",
    4: "11:40 - 12:20",
    5: "12:40 - 13:20",
    6: "13:40 - 14:20",
    7: "14:40 - 15:20",
    8: "15:30 - 16:10",
}

DBTG = TelegramAgent()
AGENT = Agent()
MAIN_MENU_MARKUP = markup_from(
    [
        [("Следующий урок", CallbackEnum.CHECK_NEXT_LESSON)],
        [
            ("Сегодня", CallbackEnum.CHECK_TODAY),
            ("Завтра", CallbackEnum.CHECK_TOMORROW),
        ],
        [(" Определенный день недели ", CallbackEnum.CHECK_CERTAIN_DAY)],
        [("Неделя", CallbackEnum.CHECK_WEEK)],
        [("Другое", CallbackEnum.MISC_MENU)],
    ]
)


texts = get_json("texts.json")
announcements = list(
    map(lambda text: " ● " + text, get_json("announcements.json")["data"])
)


def get_text(text):
    return texts[text]


def announce_bot_update(updater: Updater):
    with open(
        path.abspath(
            path.join(path.dirname(__file__), "..", "resources", "update_message.md")
        ),
        "r",
    ) as f:
        text = f.read()
    for telegram_id in DBTG.get_chats():
        logger.info(f"Send announcement to {telegram_id}")
        updater.bot.send_message(
            chat_id=telegram_id,
            text=text + get_text("restart_message"),
            parse_mode="markdown",
        )
        sleep(0.5)


def main_menu(update: Update, context, first_time=False) -> State:
    update_query(
        update=update,
        text=get_text("main_menu") if not first_time else get_text("main_menu_first"),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def start_command_handler(update: Update, context: CallbackContext) -> State:
    """Greeting new user and helping old users"""
    telegram_chat_id = update.message.chat.id

    if DBTG.check_if_user_exists(telegram_chat_id):
        # user is already registered
        update.message.reply_text(
            text=get_text("help_on_startup"),
            reply_markup=MAIN_MENU_MARKUP,
            parse_mode="markdown",
        )
        return State.MAIN_MENU  # return user to main menu
    # user is not registered, ask if user is a teacher or a student
    update.message.reply_text(
        text=get_text("greeting"),
        reply_markup=markup_from(
            [
                [("Ученик", CallbackEnum.IM_STUDENT.value)],  # buttons for students
                [("Учитель", CallbackEnum.IM_TEACHER.value)],  # and for teachers
            ]
        ),
        parse_mode="markdown",
    )
    return State.LOGIN  # as user is not registred we send him to login state


def choose_parallel(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("enter_parallel"),
        # let user enter his current course
        reply_markup=markup_from(
            [
                [
                    ("8 класс", "{}_8".format(CallbackEnum.PARALLEL.value)),
                    ("9 класс", "{}_9".format(CallbackEnum.PARALLEL.value)),
                ],
                [
                    ("10 класс", "{}_10".format(CallbackEnum.PARALLEL.value)),
                    ("11 класс", "{}_11".format(CallbackEnum.PARALLEL.value)),
                ],
            ]
        ),
    )
    return State.PARALLEL_ENTERED


def choose_letter(update: Update, context: CallbackContext) -> State:
    # scrap data from callback_data\
    parallel = update.callback_query.data.split("_")[-1]
    context.user_data["USER_PARALLEL"] = parallel  # save user data
    update_query(
        update=update,
        text=get_text("enter_letter"),
        reply_markup=markup_from(
            [
                [
                    (
                        f"{letter}",
                        "{}_{}".format(CallbackEnum.LETTER.value, letter.lower()),
                    )
                    for letter in letter_list
                ]
                for letter_list in ["АБВГДЕ", "ЖЗИЙКЛ", "МНОПРС", "ТУФХЦ", "ЧШЭЮЯ"]
            ]
        ),
    )
    return State.LETTER_ENTERED


def choose_group(update: Update, context: CallbackContext) -> State:
    letter = update.callback_query.data.split("_")[-1]
    context.user_data["USER_LETTER"] = letter

    update_query(
        update=update,
        text=get_text("enter_subclass"),
        reply_markup=markup_from(
            [
                [("1 группа", "{}_1".format(CallbackEnum.GROUP.value))],
                [("2 группа", "{}_2".format(CallbackEnum.GROUP.value))],
            ]
        ),
    )
    return State.GROUP_ENTERED


def confirm_subclass(update: Update, context: CallbackContext) -> State:
    group = update.callback_query.data.split("_")[-1]
    context.user_data["USER_GROUP"] = group

    subclass = (
        context.user_data["USER_PARALLEL"]
        + context.user_data["USER_LETTER"]
        + context.user_data["USER_GROUP"]
    )
    context.user_data["SUBCLASS"] = subclass
    update_query(
        update=update,
        text=get_text("confirm_class").format(subclass=subclass.capitalize()),
        reply_markup=markup_from(
            [
                [("Да, верно", CallbackEnum.CONFIRM_SUBCLASS.value)],
                [("Нет, я хочу изменить", CallbackEnum.CHANGE_SUBCLASS.value)],
            ]
        ),
    )
    return State.CONFIRM_SUBCLASS


def save_subclass_to_database(update: Update, context: CallbackContext) -> State:
    subclass = context.user_data["SUBCLASS"]
    telegram_id = get_telegram_id(update)
    if not DBTG.check_if_user_exists(telegram_id):
        logger.info(f"User {telegram_id} registered with subclass {subclass}")
        # this is new user, so we create new row in database
        DBTG.create_new_user(
            telegram_id=telegram_id, is_student=True, subclass=subclass
        )
    else:
        logger.info(f"User {telegram_id} changed his subclass to {subclass}")
        # this is old user, update row
        DBTG.change_subclass(telegram_id=telegram_id, subclass=subclass)
    # return main menu
    return main_menu(update, context, True)


def ask_teacher_name(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("enter_name"),
    )
    context.user_data["CALLBACK_MESSAGE"] = update.callback_query
    return State.NAME_ENTERED


def confirm_teacher_name(update: Update, context: CallbackContext) -> State:
    name = update.message.text
    if name.count(" ") >= 2:
        # Surname. N. N.
        name = "{} {}{}".format(*name.split())
    context.user_data["USER_NAME"] = name

    update.message.delete()
    context.user_data.pop("CALLBACK_MESSAGE").edit_message_text(
        text=get_text("confirm_name").format(teacher_name=name),
        reply_markup=markup_from(
            [
                [("Да, все верно", CallbackEnum.CONFIRM_NAME.value)],
                [("Нет, я хочу изменить", CallbackEnum.CHANGE_NAME.value)],
            ]
        ),
    )
    return State.CONFIRM_NAME


def save_teacher_name_to_database(update: Update, context: CallbackContext) -> State:
    name = context.user_data["USER_NAME"]
    telegram_id = get_telegram_id(update)
    if not DBTG.check_if_user_exists(telegram_id):
        # new teacher
        logger.info(f"User {telegram_id} registered with name {name}")
        DBTG.create_new_user(
            telegram_id=telegram_id, is_student=False, teacher_name=name
        )
    else:
        logger.info(f"User {telegram_id} changed his name to {name}")
        # old user
        DBTG.change_teacher_name(telegram_id=telegram_id, teacher_name=name)
    return main_menu(update, context, True)


def get_next_lesson(update: Update, context: CallbackContext) -> State:
    user = DBTG.get_user(get_telegram_id(update))
    lesson_number = get_lesson_number(datetime.now())  # current lesson
    day_of_week = get_current_day_of_week()
    if lesson_number != -1:  # find lesson
        timetable = AGENT.get_day(user, day_of_week)
        if timetable.lessons:  # there are some lessons today
            for i, lesson_t in enumerate(timetable.lessons):
                if lesson_t.lesson_number > lesson_number:  # search first after current
                    lesson = lesson_t  # found lesson
                    # check_group(timetable, i, lesson)
                    return send_lesson(update, user, lesson, day_of_week)
            else:
                timetable = AGENT.get_day(user, day_of_week + 1)
    elif datetime.now() in DateTimeRange("0:00", "8:14"):  # early morning
        timetable = AGENT.get_day(user, day_of_week)  # today
    else:  # afer lessons
        # timetable = AGENT.get_day(user, day_of_week + 1)  # next day
        days = AGENT.get_week(user)[day_of_week:]
        days.extend(AGENT.get_week(user)[: day_of_week - 1])  # next days
        for d_timetable in days:
            if d_timetable.lessons:
                day_of_week = d_timetable.day_of_week
                lesson = d_timetable.lessons[0]
                # check_group(timetable, 1, lesson)
                timetable = d_timetable
                break
    if not timetable.lessons:
        if day_of_week in [6, 7]:  # saturday without lesson or sunday
            days = AGENT.get_week(user)  # timetable for monday
            for timetable in days:
                if timetable.lessons:
                    day_of_week = timetable.day_of_week
                    lesson = timetable.lessons[0]
                    # check_group(timetable, 1, lesson)
                    return send_lesson(update, user, lesson, day_of_week)
        # wrong parameters
        text = get_text("can_not_find_next_lesson")
    else:  # there is some lessons
        lesson = timetable.lessons[0]
        # check_group(timetable, 1, lesson)
        send_lesson(update, user, lesson, timetable.day_of_week)

    # update_query(update=update, text=text, reply_markup=MAIN_MENU_MARKUP)
    return State.MAIN_MENU


def check_group(timetable, i, lesson):
    groups = [lesson.subclass]
    while (
        len(timetable.lessons) > i
        and timetable.lessons[i].lesson_number == lesson.lesson_number
    ):
        groups.append(timetable.lessons[i].subclass)
        i += 1
    lesson.subclass = ", ".join(groups)


def send_lesson(update, user, lesson, day_of_week):
    days = {
        1: "в понедельник",
        2: "во вторник",
        3: "в среду",
        4: "в четверг",
        5: "в пятницу",
        6: "в субботу",
        7: "в воскресенье",
    }

    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f'User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] asked for lessons "{days[day_of_week]}"'
    )

    text = (
        "Следующий урок "
        + days[day_of_week]
        + ".\n\n"
        + get_text("lesson_format").format(
            lesson_number=lesson.lesson_number,
            lesson_time=LESSON_TIME[lesson.lesson_number],
            subject=lesson.subject,
            cabinet=lesson.cabinet,
            misc_info=lesson.teacher if isinstance(user, Student) else lesson.subclass,
        )
    )
    update_query(update=update, text=text, reply_markup=MAIN_MENU_MARKUP)
    return State.MAIN_MENU


def get_timetable_today(update: Update, context: CallbackContext) -> State:
    user = DBTG.get_user(get_telegram_id(update))
    timetable = AGENT.get_day(user, get_current_day_of_week())

    telegram_id = get_telegram_id(update)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] asked for lessons today (DOW: {get_current_day_of_week()})"
    )

    if not timetable.lessons:
        update_query(
            update=update,
            text=get_text("no_lessons"),
            reply_markup=MAIN_MENU_MARKUP,
        )
        return State.MAIN_MENU

    update_query(
        update=update,
        text=get_text("today_timetable").format(
            lessons="\n\n".join(
                get_text("lesson_format").format(
                    lesson_number=lesson.lesson_number,
                    lesson_time=LESSON_TIME[lesson.lesson_number],
                    subject=lesson.subject,
                    cabinet=lesson.cabinet,
                    misc_info=lesson.teacher
                    if isinstance(user, Student)
                    else lesson.subclass,
                )
                for lesson in timetable.lessons
            )
        ),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def get_timetable_tommorow(update: Update, context: CallbackContext) -> State:
    user = DBTG.get_user(get_telegram_id(update))
    timetable = AGENT.get_day(user, get_current_day_of_week() % 7 + 1)

    telegram_id = get_telegram_id(update)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] asked for lessons tommorow (DOW: {get_current_day_of_week() % 7 + 1})"
    )

    if not timetable.lessons:
        update_query(
            update=update,
            text=get_text("no_lessons"),
            reply_markup=MAIN_MENU_MARKUP,
        )
        return State.MAIN_MENU

    update_query(
        update=update,
        text=get_text("tomorrow_timetable").format(
            lessons="\n\n".join(
                get_text("lesson_format").format(
                    lesson_number=lesson.lesson_number,
                    lesson_time=LESSON_TIME[lesson.lesson_number],
                    subject=lesson.subject,
                    cabinet=lesson.cabinet,
                    misc_info=lesson.teacher
                    if isinstance(user, Student)
                    else lesson.subclass,
                )
                for lesson in timetable.lessons
            )
        ),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def select_day_of_week(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("select_dayweek"),
        reply_markup=markup_from(
            [
                [("Понедельник", "{}_1".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
                [("Вторник", "{}_2".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
                [("Среда", "{}_3".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
                [("Четверг", "{}_4".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
                [("Пятница", "{}_5".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
                [("Суббота", "{}_6".format(CallbackEnum.SELECT_DAY_OF_WEEK))],
            ]
        ),
    )
    return State.SELECT_DAY_OF_WEEK


def get_timetable_certain_day(update: Update, context: CallbackContext) -> State:
    day_of_week = update.callback_query.data.split("_")[-1]
    user = DBTG.get_user(get_telegram_id(update))
    timetable = AGENT.get_day(user, int(day_of_week))
    days = {
        "1": "понедельник",
        "2": "вторник",
        "3": "среду",
        "4": "четверг",
        "5": "пятницу",
        "6": "субботу",
        "7": "воскресенье",
    }

    telegram_id = get_telegram_id(update)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] asked for lessons in certain day (DOW: {day_of_week})"
    )

    update_query(
        update=update,
        text=get_text("certain_day_timetable").format(
            day_of_week=days[day_of_week],
            lessons="\n\n".join(
                get_text("lesson_format").format(
                    lesson_number=lesson.lesson_number,
                    lesson_time=LESSON_TIME[lesson.lesson_number],
                    subject=lesson.subject,
                    cabinet=lesson.cabinet,
                    misc_info=lesson.teacher
                    if isinstance(user, Student)
                    else lesson.subclass,
                )
                for lesson in timetable.lessons
            ),
        )
        if timetable.lessons
        else "У вас нет уроков в этот день",
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def get_timetable_week(update: Update, context: CallbackContext) -> State:
    days = days = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье",
    }
    user = DBTG.get_user(get_telegram_id(update))
    timetable = AGENT.get_week(user)

    telegram_id = get_telegram_id(update)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] asked for lessons for week"
    )

    if all(map(lambda x: x.lessons != [], timetable)):
        update_query(
            update=update,
            text=get_text("check_your_info"),
            reply_markup=MAIN_MENU_MARKUP,
        )

    update_query(
        update=update,
        text="\n\n".join(
            (
                "-" * 30
                + "\n*"
                + (days[day.day_of_week] + "*" + "\n\n")
                + "\n\n".join(
                    get_text("lesson_format").format(
                        lesson_number=lesson.lesson_number,
                        lesson_time=LESSON_TIME[lesson.lesson_number],
                        subject=lesson.subject,
                        cabinet=lesson.cabinet,
                        misc_info=lesson.teacher
                        if isinstance(user, Student)
                        else lesson.subclass,
                    )
                    for lesson in day.lessons
                )
            )
            for day in filter(lambda x: x.lessons != [], timetable)
        ),
        reply_markup=MAIN_MENU_MARKUP,
    )

    return State.MAIN_MENU


def misc_menu(update: Update, context: CallbackContext) -> State:
    update_query(
        update,
        text=get_text("misc_menu"),
        reply_markup=markup_from(
            [
                [
                    ("Найти класс", CallbackEnum.FIND_SUBCLASS),
                    ("Найти учителя", CallbackEnum.FIND_TEACHER),
                ],
                [("Расписание звонков", CallbackEnum.RINGS)],
                [("Написать разработчикам", CallbackEnum.HELP)],
                [("Поддержать разработчиков", CallbackEnum.DONATE)],
                [("Вернуться в главное меню", CallbackEnum.MAIN_MENU)],
                [(" \u27A1 ", CallbackEnum.MISC_MENU_SECOND)],
            ]
        ),
    )
    return State.MISC_MENU


def misc_menu_second(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("misc_menu"),
        reply_markup=markup_from(
            [
                [("Объявления", CallbackEnum.ANNOUNCEMENTS)],
                [("Расписание столовой", CallbackEnum.CANTEEN)],
                # [("Найстройки уведомлений", CallbackEnum.SETTINGS)]
                [("Изменить ФИО/класс", CallbackEnum.CHANGE_INFORMATION)],
                [("Вернуться в главное меню", CallbackEnum.MAIN_MENU)],
                [(" \u2B05 ", CallbackEnum.MISC_MENU_FIRST)],
            ]
        ),
    )
    return State.MISC_MENU_SECOND


def find_teacher(update: Update, context: CallbackContext) -> State:
    #TODO
    return State.MISC_MENU


def find_subclass(update: Update, context: CallbackContext) -> State:
    #TODO
    return State.MISC_MENU


def announcements_handler(update: Update, context: CallbackContext) -> State:

    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] checked announcements"
    )

    update_query(
        update=update, text="\n\n".join(announcements), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU_SECOND


def donate_message(update: Update, context: CallbackContext) -> State:
    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] checked donat text"
    )

    update_query(
        update=update, text=get_text("donate_message"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def rings(update: Update, context: CallbackContext) -> State:
    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] checked rings text"
    )

    update_query(
        update=update, text=get_text("rings_timetable"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def canteen(update: Update, context: CallbackContext) -> State:
    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] checked canteen text"
    )

    update_query(
        update=update, text=get_text("canteen_timetable"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU_SECOND


def connect_to_devs(update: Update, context: CallbackContext) -> State:
    telegram_id = get_telegram_id(update)
    user = DBTG.get_user(telegram_id)
    info = user.subclass if isinstance(user, Student) else user.name
    logger.info(
        f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] checked devs info"
    )

    update_query(
        update=update,
        text=get_text("help_message").format(telegram_id=get_telegram_id(update)),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def change_info(update: Update, context: CallbackContext) -> State:
    # telegram_id = get_telegram_id(update)
    # if isinstance(DBTG.get_user(telegram_id), Student):
    #     return choose_parallel(update, context)
    # else:
    #     return ask_teacher_name(update, context)
    update_query(
        update=update,
        text=get_text("change_me"),
        reply_markup=markup_from(
            [
                [("Ученик", CallbackEnum.IM_STUDENT)],  # buttons for students
                [("Учитель", CallbackEnum.IM_TEACHER)],  # and for teachers
            ]
        ),
    )
    return State.LOGIN  # as user is not registred we send him to login state


def main_menu_distributor(update: Update, context: CallbackContext):
    event = CallbackEnum(update.callback_query.data)
    if event == CallbackEnum.CHECK_NEXT_LESSON:
        return get_next_lesson(update, context)
    elif event == CallbackEnum.CHECK_TODAY:
        return get_timetable_today(update, context)
    elif event == CallbackEnum.CHECK_TOMORROW:
        return get_timetable_tommorow(update, context)
    elif event == CallbackEnum.CHECK_CERTAIN_DAY:
        return select_day_of_week(update, context)
    elif event == CallbackEnum.CHECK_WEEK:
        return get_timetable_week(update, context)
    elif event == CallbackEnum.MISC_MENU:
        return misc_menu(update, context)
    else:
        telegram_id = get_telegram_id(update)
        user = DBTG.get_user(telegram_id)
        info = user.subclass if isinstance(user, Student) else user.name
        logger.error(
            f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] got unknown event: {event}"
        )
        return State.MAIN_MENU


def misc_menu_distributor(update: Update, context: CallbackContext):
    event = CallbackEnum(update.callback_query.data)
    if event == CallbackEnum.FIND_SUBCLASS:
        return find_subclass(update, context)
    elif event == CallbackEnum.FIND_TEACHER:
        return find_teacher(update, context)
    elif event == CallbackEnum.RINGS:
        return rings(update, context)
    elif event == CallbackEnum.HELP:
        return connect_to_devs(update, context)
    elif event == CallbackEnum.DONATE:
        return donate_message(update, context)
    elif event == CallbackEnum.MAIN_MENU:
        return main_menu(update, context)
    elif event == CallbackEnum.MISC_MENU_SECOND:
        return misc_menu_second(update, context)
    else:
        telegram_id = get_telegram_id(update)
        user = DBTG.get_user(telegram_id)
        info = user.subclass if isinstance(user, Student) else user.name
        logger.error(
            f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] got unknown event: {event}"
        )
        return State.MISC_MENU


def misc_menu_second_distributor(update: Update, context: CallbackContext):
    event = CallbackEnum(update.callback_query.data)
    if event == CallbackEnum.ANNOUNCEMENTS:
        return announcements_handler(update, context)
    elif event == CallbackEnum.CANTEEN:
        return canteen(update, context)
    elif event == CallbackEnum.CHANGE_INFORMATION:
        return change_info(update, context)
    elif event == CallbackEnum.MISC_MENU_FIRST:
        return misc_menu(update, context)
    elif event == CallbackEnum.MAIN_MENU:
        return main_menu(update, context)
    else:
        telegram_id = get_telegram_id(update)
        user = DBTG.get_user(telegram_id)
        info = user.subclass if isinstance(user, Student) else user.name
        logger.error(
            f"User {telegram_id} ({info}) [{update.callback_query.message.chat.username}] got unknown event: {event}"
        )
        return State.MISC_MENU_SECOND

from datetime import datetime
from typing import Callable

from datetimerange import DateTimeRange

from database.interface import Agent
from database.models import Student
from database.telegram import TelegramAgent
from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot.enums import CallbackEnum, State
from telegram_bot.support_functions import (
    update_query,
    get_current_day_of_week,
    get_lesson_number,
    get_telegram_id,
    get_json,
    markup_from,
)

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
announcements = get_json("announcements.json")["data"]

def get_text(text):
    return texts[text]


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
            text=get_text("help_on_startup"), reply_markup=MAIN_MENU_MARKUP
        )
        return State.MAIN_MENU  # return user to main menu
    # user is not registered, ask if user is a teacher or a student
    update.message.reply_text(
        text=get_text("greeting"),
        reply_markup=markup_from(
            [
                [("Ученик", CallbackEnum.IM_STUDENT)],  # buttons for students
                [("Учитель", CallbackEnum.IM_TEACHER)],  # and for teachers
            ]
        ),
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
                    ("8 класс", "{}_8".format(CallbackEnum.PARALLEL)),
                    ("9 класс", "{}_9".format(CallbackEnum.PARALLEL)),
                ],
                [
                    ("10 класс", "{}_10".format(CallbackEnum.PARALLEL)),
                    ("11 класс", "{}_11".format(CallbackEnum.PARALLEL)),
                ],
            ]
        ),
    )
    return State.PARALLEL_ENTERED


def choose_letter(update: Update, context: CallbackContext) -> State:
    # scrap data from callback_data
    parallel = update.callback_query.data.split("_")[-1]
    context.user_data["USER_PARALLEL"] = parallel  # save user data
    update_query(
        update=update,
        text=get_text("enter_letter"),
        reply_markup=markup_from(
            [
                [
                    (f"{letter}", "{}_{}".format(CallbackEnum.LETTER, letter))
                    for letter in letter_list
                ]
                for letter_list in ["абвгде", "жзийкл", "мнопрс", "туфхц", "чшэюя"]
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
                [("1 группа", "{}_1".format(CallbackEnum.GROUP))],
                [("2 группа", "{}_2".format(CallbackEnum.GROUP))],
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
        text=get_text("confirm_class").format(subclass=subclass),
        reply_markup=markup_from(
            [
                [("Да, верно", CallbackEnum.CONFIRM_SUBCLASS)],
                [("Нет, я хочу изменить", CallbackEnum.CHANGE_SUBCLASS)],
            ]
        ),
    )
    return State.CONFIRM_SUBCLASS


def save_subclass_to_database(update: Update, context: CallbackContext) -> State:
    subclass = context.user_data["SUBCLASS"]
    telegram_id = get_telegram_id(update)
    if not DBTG.check_if_user_exists(telegram_id):
        # this is new user, so we create new row in database
        DBTG.create_new_user(
            telegram_id=telegram_id, is_student=True, subclass=subclass
        )
    else:
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
    context.user_data["USER_NAME"] = name

    update.message.delete()
    context.user_data.pop("CALLBACK_MESSAGE").edit_message_text(
        text=get_text("confirm_name").format(teacher_name=name),
        reply_markup=markup_from(
            [
                [("Да, все верно", CallbackEnum.CONFIRM_NAME)],
                [("Нет, я хочу изменить", CallbackEnum.CHANGE_NAME)],
            ]
        ),
    )
    return State.CONFIRM_NAME


def save_teacher_name_to_database(update: Update, context: CallbackContext) -> State:
    name = context.user_data["USER_NAME"]
    telegram_id = get_telegram_id(update)
    if not DBTG.check_if_user_exists(telegram_id):
        # new teacher
        DBTG.create_new_user(
            telegram_id=telegram_id, is_student=False, teacher_name=name
        )
    else:
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
                    #check_group(timetable, i, lesson)
                    return send_lesson(update, user, lesson, day_of_week)
            else:
                timetable = AGENT.get_day(user, day_of_week + 1)
    elif datetime.now() in DateTimeRange("0:00", "8:14"):  # early morning
        timetable = AGENT.get_day(user, day_of_week)  # today
    else:  # afer lessons
        timetable = AGENT.get_day(user, day_of_week + 1)  # next day

    if not timetable.lessons:
        if day_of_week in [6, 7]:  # saturday without lesson or sunday
            day_of_week = 1
            timetable = AGENT.get_day(user, day_of_week)  # timetable for monday
            if timetable.lessons:
                lesson = timetable.lessons[0]
                #check_group(timetable, 1, lesson)
                return send_lesson(update, user, lesson, day_of_week)
        # wrong parameters
        text = get_text("can_not_find_next_lesson")
    else:  # there is some lessons
        lesson = timetable.lessons[0]
        #check_group(timetable, 1, lesson)
        send_lesson(update, user, lesson, day_of_week)

    update_query(update=update, text=text, reply_markup=MAIN_MENU_MARKUP)
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
        1: "понедельник",
        2: "вторник",
        3: "среду",
        4: "четверг",
        5: "пятницу",
        6: "субботу",
        7: "воскресенье",
    }
    text = (
        "Следующий урок в "
        + days[day_of_week]
        + ".\n\n"
        + get_text("lesson_format").format(
            lesson_number=lesson.lesson_number,
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
    timetable = AGENT.get_day(user, get_current_day_of_week()%7 + 1)

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
    timetable = AGENT.get_day(user, day_of_week)
    days = {
        "1": "понедельник",
        "2": "вторник",
        "3": "среду",
        "4": "четверг",
        "5": "пятницу",
        "6": "субботу",
        "7": "воскресенье",
    }
    update_query(
        update=update,
        text=get_text("certain_day_timetable").format(
            day_of_week=days[day_of_week],
            lessons="\n\n".join(
                get_text("lesson_format").format(
                    lesson_number=lesson.lesson_number,
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
                (days[day.day_of_week] + "\n\n")
                + "\n\n".join(
                    get_text("lesson_format").format(
                        lesson_number=lesson.lesson_number,
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
                #[
                #    ("Найти класс", CallbackEnum.FIND_SUBCLASS),
                #    ("Найти учителя", CallbackEnum.FIND_TEACHER),
                #],
                [("Обьявления", CallbackEnum.ANNOUNCEMENTS)],
                [("Полезные материалы", CallbackEnum.HELPFUL_MATERIALS)],
                [("Туториалы", CallbackEnum.TUTORIALS)],
                [
                    ("Тех. Помощь", CallbackEnum.HELP)
                ],
                [("Изменить ФИО/класс", CallbackEnum.CHANGE_INFORMATION)],
                [("Вернуться в главное меню", CallbackEnum.MAIN_MENU)],
            ]
        ),
    )
    return State.MISC_MENU


def find_teacher(update: Update, context: CallbackContext) -> State:
    return State.MISC_MENU


def find_subclass(update: Update, context: CallbackContext) -> State:
    return State.MISC_MENU


def announcements_handler(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text="\n\n".join(announcements),
        reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def helpful_materials(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("helpful_materials"),
        reply_markup=markup_from(
            [
                [("Расписание звонков", CallbackEnum.RINGS)],
                [("Расписание столовой", CallbackEnum.CARTEEN)],
            ]
        ),
    )
    return State.HELP_MENU


def tutorials(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update, text=get_text("tutorials"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def rings(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update, text=get_text("rings_timetable"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def canteen(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update, text=get_text("canteen_timetable"), reply_markup=MAIN_MENU_MARKUP
    )
    return State.MAIN_MENU


def technical_support(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=get_text("help_message").format(telegram_id=get_telegram_id(update)),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def change_info(update: Update, context: CallbackContext) -> State:
    telegram_id = get_telegram_id(update)
    if isinstance(DBTG.get_user(telegram_id), Student):
        return choose_parallel(update, context)
    else:
        return ask_teacher_name(update, context)


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
        return State.MAIN_MENU


def misc_menu_distributor(update: Update, context: CallbackContext):
    event = CallbackEnum(update.callback_query.data)
    if event == CallbackEnum.FIND_SUBCLASS:
        return find_subclass(update, context)
    elif event == CallbackEnum.FIND_TEACHER:
        return find_teacher(update, context)
    elif event == CallbackEnum.ANNOUNCEMENTS:
        return announcements_handler(update, context)
    elif event == CallbackEnum.HELPFUL_MATERIALS:
        return helpful_materials(update, context)
    elif event == CallbackEnum.HELP:
        return technical_support(update, context)
    elif event == CallbackEnum.TUTORIALS:
        return tutorials(update, context)
    elif event == CallbackEnum.CHANGE_INFORMATION:
        return change_info(update, context)
    elif event == CallbackEnum.MAIN_MENU:
        return main_menu(update, context)
    else:
        return State.MISC_MENU


def help_menu_distributor(update: Update, context: CallbackContext):
    event = CallbackEnum(update.callback_query.data)
    if event == CallbackEnum.CARTEEN:
        return canteen(update, context)
    elif event == CallbackEnum.RINGS:
        return rings(update, context)
    return State.HELP_MENU

# THIS IS DEPRECATED

from datetime import datetime
from database.interface import Agent
from database.models import Student
from database.telegram import TelegramAgent
from telegram import Update

from telegram_bot.enums import CallbackEnum, State
from telegram_bot.support_functions import (
    update_query,
    get_current_day_of_week,
    get_lesson_number,
    get_telegram_id,
    get_text,
    markup_from,
)

TGA = TelegramAgent()
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
HELP_ON_STARTUP_TEXT = get_text("help_on_startup.txt")
MAIN_MENU_TEXT = get_text("main_menu.txt")
ENTER_PARALLEL_TEXT = get_text("enter_parallel.txt")
ENTER_LETTER_TEXT = get_text("enter_letter.txt")
ENTER_SUBCLASS_TEXT = get_text("enter_subclass.txt")
CONFIRM_CLASS_TEXT = get_text("confirm_class.txt")
ENTER_NAME_TEXT = get_text("enter_name.txt")
CONFIRM_NAME_TEXT = get_text("confirm_name.txt")
MISC_MENU_TEXT = get_text("misc_menu.txt")
SELECT_DAYWEEK_TEXT = get_text("select_dayweek.txt")
HELP_MESSAGE_TEXT = get_text("help_message.txt")


def startup_handler(update: Update, context) -> State:
    """Greet new user"""
    t_id = update.message.chat.id
    if TGA.check_if_user_exists(t_id):
        update.message.reply_text(
            text=HELP_ON_STARTUP_TEXT,
            reply_markup=MAIN_MENU_MARKUP,
        )
        return State.MAIN_MENU
    keyboard = markup_from(
        [[("Ученик", CallbackEnum.IM_STUDENT)], [("Учитель", CallbackEnum.IM_TEACHER)]]
    )
    update.message.reply_text(text=get_text("greeting.txt"), reply_markup=keyboard)
    return State.LOGIN


def main_menu(update: Update, context) -> State:
    update_query(
        update,
        text=MAIN_MENU_TEXT,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def choose_parallel(update: Update, context) -> State.CHANGE_CLASS:

    update_query(
        update,
        text=ENTER_PARALLEL_TEXT,
        reply_markup=markup_from(
            [
                [("8", "8"), ("9", "9")],
                [("10", "10"), ("11", "11")],
            ]
        ),
    )
    return State.CHANGE_CLASS


def choose_letter(update: Update, context) -> State.CHANGE_CLASS:
    parallel = update.callback_query.data
    update_query(
        update,
        text=ENTER_LETTER_TEXT,
        reply_markup=markup_from(
            [
                [(f"   {letter}   ", parallel + letter) for letter in "абвгде"],
                [(f"   {letter}   ", parallel + letter) for letter in "жзийкл"],
                [(f"   {letter}   ", parallel + letter) for letter in "мнопрс"],
                [(f"   {letter}   ", parallel + letter) for letter in "туфхц"],
                [(f"   {letter}   ", parallel + letter) for letter in "чшэюя"],
            ]
        ),
    )
    return State.CHANGE_CLASS



def choose_group(update: Update, context) -> State:
    s_class = update.callback_query.data
    update_query(
        update,
        text=ENTER_SUBCLASS_TEXT,
        reply_markup=markup_from(
            [
                [("1", s_class + "1")],
                [("2", s_class + "2")],
            ]
        ),
    )
    return State.CHANGE_CLASS


def confirm_class(update: Update, context) -> State.CHANGE_CLASS:
    subclass = update.callback_query.data
    update_query(
        update,
        text=CONFIRM_CLASS_TEXT.format(subclass=subclass),
        reply_markup=markup_from(
            [
                [("Да", CallbackEnum.CONFIRM_SUBCLASS.value + f"_{subclass}")],
                [("Нет", CallbackEnum.CHANGE_SUBCLASS)],
            ]
        ),
    )
    return State.CHANGE_CLASS


def save_subclass_to_database(update: Update, context) -> State.CHANGE_CLASS:
    subclass = update.callback_query.data.split("_")[-1]
    t_id = get_telegram_id(update)
    if not TGA.check_if_user_exists(t_id):
        TGA.create_new_user(telegram_id=t_id, is_student=True, subclass=subclass)
    else:
        TGA.change_subclass(t_id, subclass)
    return main_menu(update, context)


def ask_teachers_name(update: Update, context) -> State.CHANGE_NAME:
    update_query(update, text=ENTER_NAME_TEXT)
    return State.CHANGE_NAME


def confirm_teacher_name(update: Update, context) -> State.CHANGE_NAME:
    name = update.message.text
    update.message.reply_text(
        text=CONFIRM_NAME_TEXT.format(teacher_name=name),
        reply_markup=markup_from(
            [
                [("Да", CallbackEnum.CONFIRM_NAME.value + f"_{name}")],
                [("Нет", CallbackEnum.CHANGE_NAME)],
            ]
        ),
    )
    return State.CHANGE_NAME


def save_teacher_name_to_database(update: Update, context) -> State.MAIN_MENU:
    name = update.callback_query.data.split("_")[-1]
    t_id = get_telegram_id(update)
    if not TGA.check_if_user_exists(t_id):
        TGA.create_new_user(telegram_id=t_id, is_student=False, teacher_name=name)
    else:
        TGA.change_teacher_name(t_id, name)
    return main_menu(update, context)


def misc_menu(update: Update, context) -> State.MAIN_MENU:
    update_query(
        update,
        text=MISC_MENU_TEXT,
        reply_markup=markup_from(
            [
                [
                    ("Найти класс", CallbackEnum.FIND_SUBCLASS),
                    ("Найти учителя", CallbackEnum.FIND_TEACHER),
                ],
                [("Обьявления", CallbackEnum.ANNOUNCEMENTS)],
                [("Полезные материалы", CallbackEnum.HELPFUL_LINKS)],
                [("Тех. Помощь", CallbackEnum.HELP)],
                [("Изменить ФИО/класс", CallbackEnum.CHANGE_INFORMATION)],
                [("Вернуться в главное меню", CallbackEnum.MAIN_MENU)],
            ]
        ),
    )
    return State.MISC_MENU


def get_next_lesson(update: Update, context) -> State.MAIN_MENU:
    user = TGA.get_user(get_telegram_id(update))
    lesson_number = get_lesson_number(datetime.now())
    if lesson_number == -1:
        text = "Не удалось найти следующий урок, возможно стоит опробовать эту функцию в учебное время?"
    else:
        lesson = AGENT.get_lesson(
            user,
            get_current_day_of_week(),
            lesson_number=lesson_number+1
        )
        if not lesson:
            text = "Не удалось найти следующий урок, возможно стоит опробовать эту функцию в учебное время?"
        else:
            text = f"{lesson.lesson_number}:{lesson.subject}\n{lesson.cabinet}{lesson.teacher}"
    update_query(update, text=text, reply_markup=MAIN_MENU_MARKUP)
    return State.MAIN_MENU


def get_timetable_today(update: Update, context) -> State.MAIN_MENU:
    user = TGA.get_user(get_telegram_id(update))
    timetable = AGENT.get_day(user, get_current_day_of_week())

    # get image
    text = f"День недели: {timetable.day_of_week}\n" + "\n\n".join(
        f"{lesson.lesson_number}:{lesson.subject}\n{lesson.cabinet}{lesson.teacher}"
        for lesson in timetable.lessons
    )

    update_query(
        update,
        text=text,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def get_timetable_tomorrow(update: Update, context) -> State.MAIN_MENU:
    user = TGA.get_user(get_telegram_id(update))
    timetable = AGENT.get_day(user, (get_current_day_of_week()) % 7 + 1)

    # get image
    text = f"День недели: {timetable.day_of_week}\n" + "\n\n".join(
        f"{lesson.lesson_number}:{lesson.subject}\n{lesson.cabinet} {lesson.teacher}"
        for lesson in timetable.lessons
    )

    update_query(
        update,
        text=text,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def get_week(update: Update, context) -> State.MAIN_MENU:
    user = TGA.get_user(get_telegram_id(update))
    week_timetable = AGENT.get_week(user)

    text = ("\n" + "-" * 20 + "\n\n\n").join(
        (
            f"День недели: {timetable.day_of_week}\n"
            + "\n\n".join(
                f"{lesson.lesson_number}:{lesson.subject}\n{lesson.cabinet} {lesson.teacher}"
                for lesson in timetable.lessons
            )
        )
        for timetable in week_timetable
    )

    update_query(
        update,
        text=text,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def select_dayweek(update: Update, context) -> State.MAIN_MENU:
    update_query(
        update,
        text=SELECT_DAYWEEK_TEXT,
        reply_markup=markup_from(
            [
                [("Понедельник", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_1")],
                [("Вторник", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_2")],
                [("Среда", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_3")],
                [("Четверг", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_4")],
                [("Пятница", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_5")],
                [("Суббота", f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_6")],
            ]
        ),
    )
    return State.MAIN_MENU


def get_timetable_for_certain_day(update: Update, context) -> State.MAIN_MENU:
    user = TGA.get_user(get_telegram_id(update))
    day_of_week = update.callback_query.data.split("_")[-1]

    timetable = AGENT.get_day(user, int(day_of_week))

    # get image
    text = f"День недели: {timetable.day_of_week}\n" + "\n\n".join(
        f"{lesson.lesson_number}:{lesson.subject}\n{lesson.cabinet}{lesson.teacher}"
        for lesson in timetable.lessons
    )

    update_query(
        update,
        text=text,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def change_info(update: Update, context) -> State.CHANGE_CLASS:  # or State.CHANGE_NAME
    t_id = get_telegram_id(update)
    if isinstance(TGA.get_user(t_id), Student):
        return choose_parallel(update, context)
    else:
        return ask_teachers_name(update, context)


def technical_support(update: Update, context) -> State.MAIN_MENU:
    t_id = get_telegram_id(update)
    update_query(
        update,
        text=HELP_MESSAGE_TEXT.format(telegram_id=t_id),
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU



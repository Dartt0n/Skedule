from datetime import datetime
from typing import Callable

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
    get_text,
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
HELP_ON_STARTUP_TEXT = get_text("help_on_startup.txt")
MAIN_MENU_TEXT = get_text("main_menu.txt")
ENTER_PARALLEL_TEXT = get_text("enter_parallel.txt")
ENTER_LETTER_TEXT = get_text("enter_letter.txt")
ENTER_GROUP_TEXT = get_text("enter_subclass.txt")
CONFIRM_CLASS_TEXT = get_text("confirm_class.txt")
ENTER_NAME_TEXT = get_text("enter_name.txt")
CONFIRM_NAME_TEXT = get_text("confirm_name.txt")
MISC_MENU_TEXT = get_text("misc_menu.txt")
SELECT_DAYWEEK_TEXT = get_text("select_dayweek.txt")
HELP_MESSAGE_TEXT = get_text("help_message.txt")
GREETING_TEXT = get_text("greeting.txt")


def start_command_handler(update: Update, context: CallbackContext) -> State:
    """Greeting new user and helping old users"""
    telegram_chat_id = update.message.chat.id

    if DBTG.check_if_user_exists(telegram_chat_id):
        # user is already registered
        update.message.reply_text(
            text=HELP_ON_STARTUP_TEXT, reply_markup=MAIN_MENU_MARKUP
        )
        return State.MAIN_MENU  # return user to main menu
    # user is not registered, ask if user is a teacher or a student
    update.message.reply_text(
        text=GREETING_TEXT,
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
        text=ENTER_PARALLEL_TEXT,
        # let user enter his current course
        reply_markup=markup_from(
            [
                [
                    ("8ой класс", "{}_8".format(CallbackEnum.PARALLEL)),
                    ("9ый класс", "{}_9".format(CallbackEnum.PARALLEL)),
                ],
                [
                    ("10ый класс", "{}_10".format(CallbackEnum.PARALLEL)),
                    ("11ый класс", "{}_11".format(CallbackEnum.PARALLEL)),
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
        text=ENTER_LETTER_TEXT,
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
        text=ENTER_GROUP_TEXT,
        reply_markup=markup_from(
            [
                [("1ая группа", "{}_1".format(CallbackEnum.GROUP))],
                [("2ая группа", "{}_2".format(CallbackEnum.GROUP))]
            ]
        )
    )
    return State.GROUP_ENTERED


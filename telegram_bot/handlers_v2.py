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
def get_text(text):
    return texts[text]

def start_command_handler(update: Update, context: CallbackContext) -> State:
    """Greeting new user and helping old users"""
    telegram_chat_id = get_telegram_id(update)

    if DBTG.check_if_user_exists(telegram_chat_id):
        # user is already registered
        update.message.reply_text(
            text=get_text('help_on_startup'), reply_markup=MAIN_MENU_MARKUP
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


def choose_parallel(return_to_state: State) -> Callable:
    def callback_function(update: Update, _context: CallbackContext) -> State:
        update_query(
            update=update,
            text=get_text("enter_parallel"),
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
        return return_to_state

    return callback_function


def choose_letter(return_to_state: State) -> Callable:
    def callback_function(update: Update, context: CallbackContext) -> State:
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
        return return_to_state
    return callback_function


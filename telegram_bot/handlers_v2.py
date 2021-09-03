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


def main_menu(update: Update, context) -> State:
    update_query(
        update=update,
        text=MAIN_MENU_TEXT,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return State.MAIN_MENU


def start_command_handler(update: Update, context: CallbackContext) -> State:
    """Greeting new user and helping old users"""
    telegram_chat_id = update.message.chat.id

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


def choose_parallel(update: Update, context: CallbackContext) -> State:
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
        text=ENTER_GROUP_TEXT,
        reply_markup=markup_from(
            [
                [("1ая группа", "{}_1".format(CallbackEnum.GROUP))],
                [("2ая группа", "{}_2".format(CallbackEnum.GROUP))],
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
        text=CONFIRM_CLASS_TEXT.format(subclass=subclass),
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
    return main_menu(update, context)


def ask_teacher_name(update: Update, context: CallbackContext) -> State:
    update_query(
        update=update,
        text=ENTER_NAME_TEXT,
    )
    context.user_data["CALLBACK_MESSAGE"] = update.callback_query
    return State.NAME_ENTERED


def confirm_teacher_name(update: Update, context: CallbackContext) -> State:
    name = update.message.text
    context.user_data["USER_NAME"] = name

    update.message.delete()
    context.user_data.pop("CALLBACK_MESSAGE").edit_message_text(
        text=CONFIRM_NAME_TEXT.format(teacher_name=name),
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
        DBTG.create_new_user(telegram_id=telegram_id, is_student=False, teacher_name=name)
    else:
        # old user
        DBTG.change_teacher_name(telegram_id=telegram_id, teacher_name=name)
    return main_menu(update, context)
import json
from datetime import datetime
from os import path
from typing import Dict

from datetimerange import DateTimeRange
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram_bot.enums import CallbackEnum


def get_lesson_number(time) -> int:
    """Return number of lesson (include break after that)
    if time not in study time return -1

    Args:
        time (datetime object): time for checking, basic usage: datetime.now()

    Returns:
        int: lesson number or -1 if not found
    """
    # """

    # """
    # TODO make import from table or something
    lessons_ranges = [
        DateTimeRange("8:15", "9:00"),  # 0
        DateTimeRange("9:00", "9:50"),  # 1
        DateTimeRange("9:50", "10:45"),  # 2
        DateTimeRange("10:45", "11:40"),  # 3
        DateTimeRange("11:40", "12:40"),  # 4
        DateTimeRange("12:40", "13:40"),  # 5
        DateTimeRange("13:40", "14:40"),  # 6
        DateTimeRange("14:40", "15:30"),  # 7
        DateTimeRange("15:30", "16:10"),  # 8
    ]
    for i, lesson in enumerate(lessons_ranges):
        if time in lesson:
            return i
    return -1


def markup_from(variants) -> InlineKeyboardMarkup:
    """Generate markup from variants.
    Variants must have certain structure. Firsly, variants is a list every element of which is a list too.
    variants itself contains ROWS for buttons, which are lists.
    every row contains elements - Tuple, identifing button. Numbor of buttons in row is a number of columns.
    Button is a tuple of two strings. First is a text for button, and second is callback_data
    Valid variants:
    [
        [("1-1", Callback), ("1-2", Callback)],
        [("2-1", Callback)],
        [("3-1", Callback), ("3-2", Callback), ("3-3", Callback)],
    ]

    Args:
        variants (List[List[Tuple[str, str]]]: variants for buttons

    Returns:
        InlineKeyboardMarkup: keyboard markup for message
    """
    keyboard = []
    for row in variants:
        keyboard.append([])
        for column in row:
            button_text, callback = column
            if isinstance(callback, CallbackEnum):
                callback = callback.value
            keyboard[-1].append(
                InlineKeyboardButton(text=button_text, callback_data=callback)
            )
    return InlineKeyboardMarkup(keyboard)


def get_json(filename: str) -> Dict:
    """This function read filename file as json and return it as python dict.
    This function search file name in @/resourses/ directory.

    Args:
        filename (str): Name of json file.

    Returns:
        Dict: python dict generated from json
    """
    path_to_file = path.abspath(
        path.join(path.dirname(__file__), "..", "resources", filename)
    )
    with open(path_to_file, "r") as f:
        return json.loads(f.read())


def update_query(update: Update, text: str, reply_markup: InlineKeyboardMarkup = None):
    """This function answer for user query (user will receive notification) and
    edit last callback query message with text and optional reply markup.

    Args:
        update (Update): Update instance from telegram api
        text (str): text which will be send to user
        reply_markup (InlineKeyboardMarkup, optional): Inline buttons for message. Defaults to None.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="markdown")


def get_telegram_id(update) -> int:
    """Return telegram id from update instance

    Args:
        update (Update): update instance from telegram api

    Returns:
        int: chat id
    """
    return update.callback_query.message.chat.id


def get_current_day_of_week() -> int:
    """Return current day of week

    Returns:
        int: day of week
    """
    return datetime.today().weekday() + 1

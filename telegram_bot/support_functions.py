from datetime import datetime
from os import path

from datetimerange import DateTimeRange
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram_bot.enums import CallbackEnum

import json 


def get_lesson_number(time) -> int:
    """
    Return number of lesson (include break after that)
    if time not in study time return -1
    """
    # TODO make import from table or something
    lessons_ranges = [
        DateTimeRange("9:00", "9:50"),
        DateTimeRange("9:50", "10:45"),
        DateTimeRange("10:45", "11:40"),
        DateTimeRange("11:40", "12:40"),
        DateTimeRange("12:40", "13:40"),
        DateTimeRange("13:40", "14:40"),
        DateTimeRange("14:40", "15:30"),
        DateTimeRange("15:30", "16:10"),
    ]
    for i, lesson in enumerate(lessons_ranges):
        if time in lesson:
            return i + 1
    return -1


def markup_from(variants) -> InlineKeyboardMarkup:
    """Generate InlineKeyboardMarkup from variants"""
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


def get_json(filename: str):
    path_to_file = path.abspath(
        path.join(path.dirname(__file__), "..", "resources", "texts", filename)
    )
    with open(path_to_file, "r") as f:
        return json.loads(f.read())


def update_query(update: Update, text: str, reply_markup: InlineKeyboardMarkup =None):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="markdown")


def get_telegram_id(update) -> int:
    return update.callback_query.message.chat.id


def get_current_day_of_week() -> int:
    return datetime.today().weekday() + 1

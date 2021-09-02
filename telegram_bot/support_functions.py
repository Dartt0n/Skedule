from datetime import datetime
from os import path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram_bot.enums import CallbackEnum


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


def get_text(filename: str) -> str:
    path_to_file = path.abspath(
        path.join(path.dirname(__file__), "..", "resources", "texts", filename)
    )
    with open(path_to_file, "r") as text:
        return text.read()


def edit_query(update: Update, *args, **kwargs):
    query = update.callback_query
    query.answer()
    query.edit_message_text(*args, **kwargs, parse_mode="markdown")

def get_telegram_id(update) -> int:
    return update.callback_query.message.chat.id

def get_current_day_of_week() -> int:
    return datetime.today().weekday() + 1
from datetime import datetime
from os import path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram_bot.enums import CallbackEnum

from datetimerange import DateTimeRange

def get_lesson_number(time):
    """
    Return tuple where first value is type(lesson or break)
    second value is number of lesson or break
    if time not in timetable return break 0
    """
    
    # TODO make import from table or something
    lessons_ranges = [
        DateTimeRange("9:00", "9:40"),
        DateTimeRange("9:50", "10:30"),
        DateTimeRange("10:45", "11:25"),
        DateTimeRange("11:40", "12:20"),
        DateTimeRange("12:40", "13:20"),
        DateTimeRange("13:40", "14:20"),
        DateTimeRange("14:40", "15:20"),
        DateTimeRange("15:30", "16:10"),
    ]
    breaks_ranges = [
        DateTimeRange("9:40", "9:50"),
        DateTimeRange("10:30", "10:45"),
        DateTimeRange("11:25", "11:40"),
        DateTimeRange("12:20", "12:40"),
        DateTimeRange("13:20", "13:40"),
        DateTimeRange("14:20", "14:40"),
        DateTimeRange("15:20", "15:30"),
    ]

    for i, lesson in enumerate(lessons_ranges):
        if time in lesson:
            return 'lesson', i+1
    for i, break_ in enumerate(breaks_ranges):
        if time in break_:
            return 'break', i+1
        
    return 'break', 0


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
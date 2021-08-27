from telegram import Update
from enums import State, CallbackEnum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from os import path


# COLUMNS AND ROWS MANAGEMENT IN TELEGRAM
#                                                    [    1    ]
#                                                    [2] [3] [4]
# ['1', ['2', '3', '4'], ['5'], ['6', '7'], '8'] =>  [    5    ]
#                                                    [ 5 ] [ 6 ]
#                                                    [    7    ]
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


def edit_query(update, *args, **kwargs):
    query = update.callback_query
    query.answer()
    query.edit_message_text(*args, **kwargs)


def startup_handler(update: Update, *args) -> State:
    """Greet new user"""
    # check if user is registered, if it is, skip
    keyboard = markup_from(
        [[("Ученик", CallbackEnum.IM_STUDENT)], [("Учитель", CallbackEnum.IM_TEACHER)]]
    )
    update.message.reply_text(text=get_text("greeting.txt"), reply_markup=keyboard)
    return State.LOGIN


def main_menu(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("main_menu_text.txt"),
        reply_markup=markup_from(
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
        ),
    )
    return State.MAIN_MENU


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- LOGIN -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def ask_teacher_save_name(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("save_teacher_name.txt"),
        reply_markup=markup_from(
            [
                [("Да", CallbackEnum.SAVE_NAME)],
                [("Нет", CallbackEnum.NOT_SAVE_NAME)],
            ]
        ),
    )
    return State.CHANGE_NAME


def ask_student_save_class(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("save_student_class.txt"),
        reply_markup=markup_from(
            [
                [("Да", CallbackEnum.SAVE_CLASS)],
                [("Нет", CallbackEnum.NOT_SAVE_CLASS)],
            ]
        ),
    )
    return State.CHANGE_CLASS


def not_save_subclass(update: Update, *args) -> State:
    return main_menu(update, *args)


def ask_parallel(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("enter_parallel.txt"),
        reply_markup=markup_from(
            [
                [("8", "8"), ("9", "9")],
                [("10", "10"), ("11", "11")],
            ]
        ),
    )
    return State.CHANGE_CLASS


def ask_letter(update: Update, *args) -> State:
    parallel = update.callback_query.data
    edit_query(
        update,
        text=get_text("enter_letter.txt"),
        reply_markup=markup_from(
            [
                [(letter, parallel + letter) for letter in "абвгдеж"],
                [(letter, parallel + letter) for letter in "зийклмн"],
                [(letter, parallel + letter) for letter in "опрстуф"],
                [(letter, parallel + letter) for letter in "хцчшэюя"],
            ]
        ),
    )
    return State.CHANGE_CLASS


def ask_group(update: Update, *args) -> State:
    s_class = update.callback_query.data
    edit_query(
        update,
        text=get_text("enter_letter.txt"),
        reply_markup=markup_from(
            [
                [("1", s_class + "1")],
                [("2", s_class + "2")],
            ]
        ),
    )
    return State.CHANGE_CLASS


def confirm_class(update: Update, *args) -> State:
    subclass = update.callback_query.data
    # TODO save letter
    edit_query(
        update,
        text=get_text("confirm_class.txt") + subclass,
        reply_markup=markup_from(
            [
                [("Да", CallbackEnum.CONFIRM_SUBCLASS)],
                [("Нет", CallbackEnum.CHANGE_SUBCLASS)],
            ]
        ),
    )
    return State.CHANGE_CLASS


def save_subclass(update: Update, *args) -> State:
    # TODO save to db
    return main_menu(update, *args)


def ask_teachers_name(update: Update, *args) -> State:
    edit_query(update, text=get_text("enter_name.txt"))
    return State.CHANGE_NAME


def not_save_name(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("main_menu_text.txt"),
        reply_markup=markup_from(
            [
                [
                    ("Следующий урок", CallbackEnum.CHECK_NEXT_LESSON),
                    ("Сегодня", CallbackEnum.CHECK_TODAY),
                ],
                [
                    ("Завтра", CallbackEnum.CHECK_TOMORROW),
                    ("Неделя", CallbackEnum.CHECK_WEEK),
                ],
                [("Определенный день недели", CallbackEnum.CHECK_CERTAIN_DAY)],
                [("Другое", CallbackEnum.MISC_MENU)],
            ]
        ),
    )
    return State.MAIN_MENU


def confirm_teacher_name(update: Update, *args) -> State:
    name = update.message.text
    update.message.reply_text(
        text=get_text("confirm_name.txt") + name,
        reply_markup=markup_from(
            [[("Да", CallbackEnum.CONFIRM_NAME)], [("Нет", CallbackEnum.CHANGE_NAME)]]
        ),
    )
    return State.CHANGE_NAME


def save_teacher_name(update: Update, *args) -> State:
    # TODO save to bd
    return main_menu(update, *args)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- MAIN MENU -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-s
def misc_menu(update: Update, *args) -> State:
    edit_query(
        update,
        text=get_text("misc_menu.txt"),
        reply_markup=markup_from(
            [
                [
                    ("Найти класс", CallbackEnum.FIND_SUBCLASS),
                    ("Найти учителя", CallbackEnum.FIND_TEACHER),
                ],
                [("Обьявления", CallbackEnum.ANNOUNCEMENTS)],
                [("Полезные материалы", CallbackEnum.HELPFUL_LINKS)],
                [("Помощь", CallbackEnum.HELP)],
                [("Изменить ФИО/класс", CallbackEnum.CHANGE_INFORMATION)],
            ]
        ),
    )

from dataclasses import dataclass
from callback import CallbackEnum
from typing import Callable, List, Tuple
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from os import path


@dataclass
class EventHandler:
    event: str
    func: Callable

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


# turn function into EventHandler object
def event(event: str):
    def decorator(func: Callable):
        def wrapper():
            event_handler = EventHandler(event, func)
            return event_handler
        return wrapper
    return decorator


# save all object i file before implementing functions
globals_before_impl = set(globals().keys())
# =========================== SUPPORT FUNCTIONS ================================

# COLUMNS AND ROWS MANAGEMENT IN TELEGRAM
#  ['1', ['2', '3']] => [  1  ]
#                       [2] [3]
# ['1', '2'] => [ 1 ]
#               [ 2 ]
# ['1', ['2', '3', '4'], ['5', '6'], '7'] => [    1    ]
#                                            [2] [3] [4]
#                                            [ 5 ] [ 6 ]
#                                            [    7    ]
def _generate_markup(
    variants: List[List[Tuple[str, CallbackEnum]]]
) -> InlineKeyboardMarkup:
    """Generate InlineKeyboardMarkup from variants"""
    keyboard = []
    for row in variants:
        keyboard.append([])
        for column in row:
            button_text, callback = column
            keyboard[-1].append(InlineKeyboardButton(text=button_text, callback_data=callback.value))
    return InlineKeyboardMarkup(keyboard)

def _get_text(filename: str) -> str:
    path_to_file = path.abspath(path.join(path.dirname(__file__), '..', 'resources', 'texts', filename))
    with open(path_to_file, 'r') as text:
        return text.read()

# ========================== WRITE HANDLERS HERE ===============================


@event("start")
def startup_handler(update: Update, _context: CallbackContext) -> None:
    """Greet new user"""
    keyboard = _generate_markup(
        [
            [("Ученик", CallbackEnum.IM_STUDENT)],
            [("Учитель", CallbackEnum.IM_TEACHER)]
        ]
    )
    update.message.reply_text(text=_get_text('greeting.txt'), reply_markup=keyboard)


@event("callback")
def callback_query_handler(update: Update, _context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {CallbackEnum(query.data).name}")


# ==============================================================================

# substract from set of implemented functions names implemented before (globals_before_impl)
# and variable globals_before_impl itself
impl_names = set(globals().keys()) - globals_before_impl - {"globals_before_impl"}
# list of pointers to functions
implemented_handlers: List[EventHandler] = []  # {}
# iterate over new variables (and functions)
for name in impl_names:
    object = globals()[name]
    # check if object is function and if it is not private
    if callable(object) and name[0] != "_":
        # save function
        # implemented_handlers[name] = object() # for dictionary
        implemented_handlers.append(object())  # <- run decorator
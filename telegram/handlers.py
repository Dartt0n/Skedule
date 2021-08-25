from dataclasses import dataclass
from typing import Callable, List
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

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

def _generate_markup(variants: List[List[str]]) -> InlineKeyboardMarkup:
    """Generate InlineKeyboardMarkup from variants"""
    #  ['1', ['2', '3']] => [  1  ]
    #                       [2] [3]
    # ['1', '2'] => [ 1 ]
    #               [ 2 ]
    # ['1', ['2', '3', '4'], ['5', '6'], '7'] => [    1    ]
    #                                            [2] [3] [4]
    #                                            [ 5 ] [ 6 ]
    #                                            [    7    ]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(button, callback_data=button) for button in row]
        for row in variants
    ])

# ========================== WRITE HANDLERS HERE ===============================

@event('start')
def startup_handler(update: Update, _context: CallbackContext) -> None:
    """Greet new user"""
    keyboard = _generate_markup([['Ученик'], ['Учитель']])
    update.message.reply_text(text="*place greet text here*", reply_markup=keyboard)

@event('callback')
def callback_query_handler(update: Update, _context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    print(query)
    query.edit_message_text(text=f"Selected option: {query.data}")

# ==============================================================================

# substract from set of implemented functions names implemented before (globals_before_impl)
# and variable globals_before_impl itself
impl_names = set(globals().keys()) - globals_before_impl - {"globals_before_impl"}
# list of pointers to functions 
implemented_handlers: List[EventHandler] = [] # {}
# iterate over new variables (and functions)
for name in impl_names:
    object = globals()[name]
    # check if object is function and if it is not private
    if callable(object) and name[0] != "_":
        # save function
        # implemented_handlers[name] = object() # for dictionary
        implemented_handlers.append(object()) # <- run decorator


if __name__ == "__main__":
    # show handlers info
    for handler in implemented_handlers:
        handler()
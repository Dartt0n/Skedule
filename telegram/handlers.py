from dataclasses import dataclass
from typing import Callable

@dataclass
class EventHandler:
    event: str
    handler: Callable

    def __call__(self, *args, **kwargs):
        self.handler(*args, **kwargs)
    
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

# ========================== WRITE HANDLERS HERE ===============================

@event('start')
def startup_handler():
    print("Starting...")

# ==============================================================================

# substract from set of implemented functions names implemented before (globals_before_impl)
# and variable globals_before_impl itself
impl_names = set(globals().keys()) - globals_before_impl - {"globals_before_impl"}
# list of pointers to functions 
implemented_handlers = [] # {}
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
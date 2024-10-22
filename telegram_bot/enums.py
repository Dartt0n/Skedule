from enum import Enum, unique, auto


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class CallbackEnum(AutoName):
    # student replies
    IM_STUDENT = auto()
    SAVE_CLASS = auto()
    NOT_SAVE_CLASS = auto()
    PARALLEL = auto()
    LETTER = auto()
    GROUP = auto()
    CONFIRM_SUBCLASS = auto()
    CHANGE_SUBCLASS = auto()
    # teacher replies
    IM_TEACHER = auto()
    SAVE_NAME = auto()
    NOT_SAVE_NAME = auto()
    CONFIRM_NAME = auto()
    CHANGE_NAME = auto()
    # main menu
    CHECK_NEXT_LESSON = auto()
    CHECK_WEEK = auto()
    CHECK_TODAY = auto()
    CHECK_TOMORROW = auto()
    CHECK_CERTAIN_DAY = auto()
    SELECT_DAY_OF_WEEK = auto()
    MISC_MENU = auto()
    # misc menu
    FIND_SUBCLASS = auto()
    FIND_TEACHER = auto()
    ANNOUNCEMENTS = auto()
    HELPFUL_MATERIALS = auto()
    HELP = auto()
    MAIN_MENU = auto()
    CHANGE_INFORMATION = auto()
    # find class
    FIND_SUBCLASS_NOW = auto()
    FIND_SUBCLASS_NEXT_LESSON = auto()
    FIND_SUBCLASS_TODAY = auto()
    FIND_SUBCLASS_WEEK = auto()
    FIND_SUBCLASS_CERTAIN_DAY = auto()
    # find teacher
    FIND_TEACHER_NOW = auto()
    FIND_TEACHER_NEXT_LESSON = auto()
    FIND_TEACHER_TODAY = auto()
    FIND_TEACHER_WEEK = auto()
    FIND_TEACHER_CERTAIN_DAY = auto()
    # help menu
    TECHNICAL_SUPPORT = auto()
    DONATE = auto()
    EXAMPLES = auto()
    FAQ = auto()
    CANTEEN = auto()
    RINGS = auto()
    #
    MISC_MENU_FIRST = auto()
    MISC_MENU_SECOND = auto()


class State(AutoName):
    MAIN_MENU = auto()
    LOGIN = auto()
    MISC_MENU = auto()
    PARALLEL_ENTERED = auto()
    LETTER_ENTERED = auto()
    GROUP_ENTERED = auto()
    CONFIRM_SUBCLASS = auto()
    NAME_ENTERED = auto()
    CONFIRM_NAME = auto()
    SELECT_DAY_OF_WEEK = auto()
    MISC_MENU_SECOND = auto()
    SEARCH_PARALLLEL_ENTERED = auto()
    SEARCH_LETTER_ENTERED = auto()
    SEARCH_SUBCLASS = auto()
    SEARCH_SUBCLASS_MENU = auto()
    SEARCH_FOR_DAY_OF_WEEK = auto()
    SEARCH_NAME_ENTERED = auto()
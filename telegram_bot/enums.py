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
    HELPFUL_LINKS = auto()
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
    TUTORIALS = auto()
    EXAMPLES = auto()
    FAQ = auto()


class State(AutoName):
    MAIN_MENU = auto()
    LOGIN = auto()
    PARALLEL_ENTERED = auto()
    LETTER_ENTERED = auto()
    GROUP_ENTERED = auto()
    CONFIRM_SUBCLASS = auto()
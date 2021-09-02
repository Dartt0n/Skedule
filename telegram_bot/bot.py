from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from telegram_bot.enums import State, CallbackEnum
import telegram_bot.handlers as handlers
from jproperties import Properties

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def pattern(event: CallbackEnum):
    return "^" + event.value + "$"


def run() -> None:
    """Run the bot."""
    properties = Properties()
    with open(".properties", "rb") as config:
        properties.load(config)
    # Create the Updater and pass it your bot's token.
    updater = Updater(properties["TG_TOKEN"].data)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", handlers.startup_handler)],
        states={
            State.LOGIN: [
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.IM_TEACHER),
                    callback=handlers.ask_teachers_name,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.IM_STUDENT),
                    callback=handlers.choose_parallel,
                ),
            ],
            State.CHANGE_NAME: [
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHANGE_NAME),
                    callback=handlers.ask_teachers_name,
                ),
                MessageHandler(
                    filters=Filters.regex(
                        f"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]*)?\s[А-ЯЁ]\.\s?[А-ЯЁ]\.$"
                    ),  # teachers names
                    callback=handlers.confirm_teacher_name,
                ),
                CallbackQueryHandler(
                    pattern="^" + CallbackEnum.CONFIRM_NAME.value,
                    callback=handlers.save_teacher_name_to_database,
                ),
            ],
            State.CHANGE_CLASS: [
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.SAVE_CLASS),
                    callback=handlers.choose_parallel,
                ),
                CallbackQueryHandler(
                    pattern=r"([0-9]|10|11)$",  # entered parallel
                    callback=handlers.choose_letter,
                ),
                CallbackQueryHandler(
                    pattern="([0-9]|10|11)[а-я]$",  # entered letter
                    callback=handlers.choose_group,
                ),
                CallbackQueryHandler(
                    pattern="([0-9]|10|11)[а-я](1|2)$",  # entered group
                    callback=handlers.confirm_class,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHANGE_SUBCLASS),
                    callback=handlers.choose_parallel,
                ),
                CallbackQueryHandler(
                    pattern="^" + CallbackEnum.CONFIRM_SUBCLASS.value,
                    callback=handlers.save_subclass_to_database,
                ),
            ],
            State.MAIN_MENU: [
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.MISC_MENU), callback=handlers.misc_menu
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.MAIN_MENU), callback=handlers.main_menu
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHECK_TODAY),
                    callback=handlers.get_timetable_today,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHECK_TOMORROW),
                    callback=handlers.get_timetable_tomorrow,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHECK_WEEK), callback=handlers.get_week
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHECK_CERTAIN_DAY),
                    callback=handlers.select_dayweek,
                ),
                CallbackQueryHandler(
                    pattern=f"{CallbackEnum.SELECT_DAY_OF_WEEK.value}_[1-7]",
                    callback=handlers.get_timetable_for_certain_day,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHECK_NEXT_LESSON),
                    callback=handlers.get_next_lesson,
                ),
            ],
            State.MISC_MENU: [
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.CHANGE_INFORMATION),
                    callback=handlers.change_info,
                ),
                CallbackQueryHandler(
                    pattern=pattern(CallbackEnum.HELP),
                    callback=handlers.technical_support,
                ),
            ],
            State.FIND_CLASS: [],
            State.FIND_TEACHER: [],
        },
        fallbacks=[CommandHandler("start", handlers.startup_handler)],
    )
    updater.dispatcher.add_handler(conversation_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

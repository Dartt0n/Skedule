from telegram.ext.callbackcontext import CallbackContext
from database.telegram import load_profile
from logger_config import logger

from jproperties import Properties
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

import telegram_bot.handlers_v2 as handlers
from telegram_bot.enums import CallbackEnum, State
from os import path


TOKEN_INFO = {"users": "TG_TOKEN", "debug_users": "TG_TEST_TOKEN"}


def pattern(event: CallbackEnum):
    return "^" + event.value + "$"


def error_handler(update, error: CallbackContext):
    logger.error(f"{error.error}")


def run() -> None:
    """Run the bot."""
    logger.info("Loading properties")
    properties = Properties()
    with open(
        path.abspath(path.join(path.dirname(__file__), "..", ".properties")), "rb"
    ) as config:
        properties.load(config)
    # Create the Updater and pass it your bot's token.
    profile = load_profile()
    logger.info(f"Loading token: {TOKEN_INFO[profile]}")
    updater = Updater(properties[TOKEN_INFO[profile]].data)

    handlers.announce_bot_update(updater)

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("start", handlers.start_command_handler),
            ],
            states={
                State.LOGIN: [
                    CallbackQueryHandler(
                        # this callback will be called when user press teacher button while in login state
                        pattern=pattern(CallbackEnum.IM_TEACHER),
                        callback=handlers.ask_teacher_name,
                    ),
                    CallbackQueryHandler(
                        # this callback will be called when user press student button while in login state
                        pattern=pattern(CallbackEnum.IM_STUDENT),
                        callback=handlers.choose_parallel,
                    ),
                ],
                State.PARALLEL_ENTERED: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.PARALLEL.value}_([0-9]|10|11)$",
                        callback=handlers.choose_letter,
                    ),
                ],
                State.LETTER_ENTERED: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.LETTER.value}",
                        callback=handlers.choose_group,
                    )
                ],
                State.GROUP_ENTERED: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.GROUP.value}",
                        callback=handlers.confirm_subclass,
                    )
                ],
                State.CONFIRM_SUBCLASS: [
                    CallbackQueryHandler(
                        pattern=pattern(CallbackEnum.CONFIRM_SUBCLASS),
                        callback=handlers.save_subclass_to_database,
                    ),
                    CallbackQueryHandler(
                        # if user want to change class send him to queue again
                        pattern=pattern(CallbackEnum.CHANGE_SUBCLASS),
                        callback=lambda update, context: handlers.choose_parallel(
                            update, context
                        ),
                    ),
                ],
                State.NAME_ENTERED: [
                    MessageHandler(
                        Filters.regex(
                            f"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]*)?\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.\s*$"
                        ),
                        handlers.confirm_teacher_name,
                    ),
                    MessageHandler(Filters.text, handlers.wrong_format_name),
                ],
                State.CONFIRM_NAME: [
                    CallbackQueryHandler(
                        pattern=pattern(CallbackEnum.CONFIRM_NAME),
                        callback=handlers.save_teacher_name_to_database,
                    ),
                    CallbackQueryHandler(
                        pattern=pattern(CallbackEnum.CHANGE_NAME),
                        callback=lambda update, context: handlers.ask_teacher_name(
                            update, context
                        ),
                    ),
                ],
                State.MAIN_MENU: [CallbackQueryHandler(handlers.main_menu_distributor)],
                State.MISC_MENU: [CallbackQueryHandler(handlers.misc_menu_distributor)],
                State.SELECT_DAY_OF_WEEK: [
                    CallbackQueryHandler(
                        callback=handlers.get_timetable_certain_day,
                    )
                ],
                State.MISC_MENU_SECOND: [
                    CallbackQueryHandler(handlers.misc_menu_second_distributor)
                ],
                State.SEARCH_PARALLLEL_ENTERED: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.PARALLEL.value}_([0-9]|10|11)$",
                        callback=handlers.choose_letter_for_search,
                    )
                ],
                State.SEARCH_LETTER_ENTERED: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.LETTER.value}",
                        callback=handlers.choose_group_for_search,
                    )
                ],
                State.SEARCH_SUBCLASS: [
                    CallbackQueryHandler(
                        pattern=f"^{CallbackEnum.GROUP.value}",
                        callback=handlers.search_subclass,
                    )
                ],
                State.SEARCH_SUBCLASS_MENU: [
                    CallbackQueryHandler(handlers.search_menu_distribution)
                ],
                State.SEARCH_FOR_DAY_OF_WEEK: [
                    CallbackQueryHandler(
                        callback=handlers.search_for_day_of_week,
                    )
                ],
                State.SEARCH_NAME_ENTERED: [
                    MessageHandler(
                        filters=Filters.regex(
                            f"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]*)?\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.\s*$"
                        ),
                        callback=handlers.search_name_entered,
                    ),
                    MessageHandler(Filters.text, handlers.wrong_search_name),
                ],
            },
            fallbacks=[CommandHandler("start", handlers.start_command_handler)],
        )
    )

    updater.dispatcher.add_error_handler(error_handler)
    # Start the Bot
    updater.start_polling()
    updater.idle()

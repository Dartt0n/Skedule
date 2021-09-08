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


def error_handler(update, error):
    logger.info("ERROR: {error}")


def run() -> None:
    """Run the bot."""
    logger.info("Loading properties")
    properties = Properties()
    with open(
        path.abspath(path.join(path.dirname(__file__), "..", ".properties")), "rb"
    ) as config:
        properties.load(config)
    # Create the Updater and pass it your bot's token.
    logger.info(f"Loading token: {TOKEN_INFO[load_profile()]}")
    updater = Updater(properties[TOKEN_INFO[load_profile()]].data)
    logger.info(f"Loaded: {properties[TOKEN_INFO[load_profile()]].data}")

    for _ in range(10):
        handlers.announce_bot_restart(updater)
    
    logger.info(f"Send announce message")
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
                        callback=handlers.confirm_subclass)],
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
                    )
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
                    CallbackQueryHandler(handlers.get_timetable_certain_day)
                ],
                State.HELP_MENU: [CallbackQueryHandler(handlers.help_menu_distributor)],
            },
            fallbacks=[CommandHandler("start", handlers.start_command_handler)],
        )
    )
    updater.dispatcher.add_error_handler(lambda *args: None)

    # Start the Bot
    updater.start_polling()
    updater.idle()

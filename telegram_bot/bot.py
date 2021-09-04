from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    handler,
)
from telegram_bot.enums import State, CallbackEnum
import telegram_bot.handlers_v2 as handlers
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

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", handlers.start_command_handler)],
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
                State.PARALLEL_ENTERED: [CallbackQueryHandler(handlers.choose_letter)],
                State.LETTER_ENTERED: [CallbackQueryHandler(handlers.choose_group)],
                State.LETTER_ENTERED: [CallbackQueryHandler(handlers.choose_group)],
                State.GROUP_ENTERED: [CallbackQueryHandler(handlers.confirm_subclass)],
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
                    MessageHandler(Filters.text, handlers.confirm_teacher_name)
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

    # Start the Bot
    updater.start_polling()
    updater.idle()

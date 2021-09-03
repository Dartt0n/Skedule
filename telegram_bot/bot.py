from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
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
                        pattern="^{}$".format(CallbackEnum.IM_TEACHER),
                        callback=None,  # TODO create function for teachers
                    ),
                    CallbackQueryHandler(
                        # this callback will be called when user press student button while in login state
                        pattern="^{}$".format(CallbackEnum.IM_STUDENT),
                        callback=handlers.choose_parallel,
                    ),
                ],
                State.PARALLEL_ENTERED: [CallbackQueryHandler(handlers.choose_letter)],
                State.LETTER_ENTERED: [CallbackQueryHandler(handlers.choose_group)],
                State.LETTER_ENTERED: [CallbackQueryHandler(handlers.choose_group)],
                
            },
            fallbacks=[],
        )
    )

    # Start the Bot
    updater.start_polling()
    updater.idle()

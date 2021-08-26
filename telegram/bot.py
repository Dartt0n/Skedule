from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)
from enums import State, CallbackEnum
import handlers
from jproperties import Properties

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def pattern(event: CallbackEnum):
    return "^" + event.value + "$"


def main() -> None:
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
                    handlers.teacher, pattern=pattern(CallbackEnum.IM_TEACHER)
                ),
                CallbackQueryHandler(
                    handlers.student, pattern=pattern(CallbackEnum.IM_STUDENT)
                ),
            ],
            State.CHANGE_NAME: [],
            State.CHANGE_CLASS: [
                CallbackQueryHandler(
                    handlers.not_save_subclass,
                    pattern=pattern(CallbackEnum.NOT_SAVE_CLASS),
                ),
                CallbackQueryHandler(
                    handlers.save_parallel, pattern=pattern(CallbackEnum.SAVE_CLASS)
                ),
                CallbackQueryHandler(handlers.save_letter, pattern=r"(8|9|10|11)$"),
                CallbackQueryHandler(
                    handlers.save_group, pattern="(8|9|10|11)[а-я]$"
                ),
                CallbackQueryHandler(
                    handlers.confirm_class, pattern="(8|9|10|11)[а-я](1|2)$"
                ),
                CallbackQueryHandler(
                    handlers.save_parallel, pattern=pattern(CallbackEnum.CHANGE_SUBCLASS)
                ),
                CallbackQueryHandler(
                    handlers.save_subclass, pattern=pattern(CallbackEnum.CONFIRM_SUBCLASS)
                ),
            ],
            State.MAIN_MENU: [],
        },
        fallbacks=[CommandHandler("start", handlers.startup_handler)],
    )
    updater.dispatcher.add_handler(conversation_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

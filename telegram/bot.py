from telegram import Update
from telegram.ext import (
    Updater,
    CallbackContext,
    PicklePersistence,
    CommandHandler,
)
from jproperties import Properties
from os import path


# handlers

def start(update: Update, context: CallbackContext) -> None:
    """
    Function for greeting users
    """
    update.message.reply_text(
        "Hello, I`m bot",
    )


def main() -> None:
    """
    Run the bot
    """

    # python file should be launched from root directory
    DIR = path.abspath(".")

    # loading config file
    properties = Properties()
    with open(path.join(DIR, ".properties"), "rb") as config_file:
        properties.load(config_file)
    # getting token from config
    TG_TOKEN = properties["TG_TOKEN"].data

    # we use pickle dump to store every inline answer
    persistence = PicklePersistence(
        filename="telegram_dump.pickle", store_callback_data=True
    )

    updater = Updater(TG_TOKEN, persistence=persistence, arbitrary_callback_data=True)
    dispatcher = updater.dispatcher
    # addint handlers to the bot
    dispatcher.add_handler(CommandHandler("start", start))

    # start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

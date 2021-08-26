from telegram.ext import Updater, CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from handlers import implemented_handlers
from jproperties import Properties


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """Run the bot."""
    properties = Properties()
    with open('.properties' , 'rb') as config:
        properties.load(config)
    # Create the Updater and pass it your bot's token.
    updater = Updater(properties["TG_TOKEN"].data)

    for handler in implemented_handlers:
        if handler.event == "callback":
            handler = CallbackQueryHandler(handler)
        else:
            handler = CommandHandler(handler.event, handler.func)
        updater.dispatcher.add_handler(handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
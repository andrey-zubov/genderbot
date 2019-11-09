import logging
import os
import sys

import django
from telegram import ReplyKeyboardMarkup, ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.expanduser(BASE_DIR)
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import TelegramBot
from help_bot.telega_logic import keyboard_button
from help_bot.utility import time_it

from functools import wraps


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


# def echo(update, context):
#     print("telega.echo(); chat_id: %s\nin_message: %s" % (update.message.chat_id, update.message.text))
#     context.bot.send_message(
#         chat_id=update.message.chat_id,
#         text=update.message.text
#     )


@time_it
@send_action(ChatAction.TYPING)
def start(update, context):
    c_id = update.message.chat_id

    logger = logging.getLogger(__name__)
    try:
        key_bord_btn, help_text = keyboard_button(update.message.text, c_id)
    except Exception as ex:
        logger.exception("Exception TelegramBot.start().\n%s" % ex)
    else:
        context.bot.send_message(
            chat_id=c_id,
            text=help_text,
            reply_markup=ReplyKeyboardMarkup(key_bord_btn, resize_keyboard=True),
        )


@time_it
@send_action(ChatAction.TYPING)
def key_bord(update, context):
    c_id = update.message.chat_id

    try:
        key_bord_btn, help_text = keyboard_button(update.message.text, c_id)
    except Exception as ex:
        logger = logging.getLogger(__name__)
        logger.exception("Exception TelegramBot.key_bord().\n%s" % ex)
    else:
        context.bot.send_message(
            chat_id=c_id,
            text=help_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=ReplyKeyboardMarkup(key_bord_btn, resize_keyboard=True),
        )


def go_go_bot():
    print("telegram.go_go_bot()")

    try:
        bot = TelegramBot.objects.get(in_work=True)
        print('bot_name: %s' % bot.name)
    except Exception as ex:
        logger = logging.getLogger(__name__)
        logger.exception("Exception TelegramBot not found!\n%s" % ex)
    else:
        updater = Updater(token=bot.token, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start)
        # echo_handler = MessageHandler(Filters.text, echo)
        # get_coords = MessageHandler(Filters.location, coords)
        ask_help = MessageHandler(Filters.text, key_bord)

        dispatcher.add_handler(start_handler)
        # dispatcher.add_handler(echo_handler)
        # dispatcher.add_handler(get_coords)
        dispatcher.add_handler(ask_help)

        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            level=logging.INFO)

        updater.start_polling()


if __name__ == "__main__":
    go_go_bot()

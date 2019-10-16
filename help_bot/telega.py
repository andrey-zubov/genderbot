import logging
import os
import sys
from time import perf_counter

import django
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(re.match(pattern='(.+HelpBot)', string=BASE_DIR))
path = os.path.expanduser(BASE_DIR)
if path not in sys.path:
    sys.path.insert(0, path)
# os.environ['DJANGO_SETTINGS_MODULE'] = 'HelpBot.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import TelegramBot
from help_bot.telega_logic import keyboard_button


def sey_hello(bot, update):
    print("chat_id: %s" % update.message.chat_id)
    print("in_message: %s" % update.message.text)

    update.message.reply_text(
        "Hello %s" % update.message.from_user.first_name
    )


def echo(update, context):
    print("telega.echo(); chat_id: %s\nin_message: %s" % (update.message.chat_id, update.message.text))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text
    )


def start(update, context):
    time_0 = perf_counter()
    c_id = update.message.chat_id
    print("telega.start(); chat_id: %s" % (c_id,))

    key_bord_btn, help_text = keyboard_button(update.message.text, c_id)

    context.bot.send_message(
        chat_id=c_id,
        text=help_text,
        reply_markup=ReplyKeyboardMarkup(key_bord_btn, one_time_keyboard=True),
    )
    print("TIME start() = %s\n" % (perf_counter() - time_0))
    """
    02.10 21:10 - TIME start() = 1.7262450889975298
    """


def coords(update, context):
    time_0 = perf_counter()
    c_id = update.message.chat_id
    print("telega.coords(); chat_id: %s\nin_message: %s" % (c_id, update.message.text))

    lat = float(update.message.location.latitude)
    lng = float(update.message.location.longitude)
    print("coord: %s, %s" % (lat, lng))

    context.bot.send_message(
        chat_id=c_id,
        text="lat: %s, lng: %s" % (lat, lng),
    )
    print("TIME coords() = %s\n" % (perf_counter() - time_0))
    """
    02.10 21:50 - TIME coords() = 2.1390733160005766
    """


def key_bord(update, context):
    time_0 = perf_counter()
    c_id = update.message.chat_id
    print("telega.key_bord(); chat_id: %s" % (c_id,))

    key_bord_btn, help_text = keyboard_button(update.message.text, c_id)

    context.bot.send_message(
        chat_id=c_id,
        text=help_text,
        reply_markup=ReplyKeyboardMarkup(key_bord_btn, one_time_keyboard=True),
    )

    print("TIME key_bord() = %s\n" % (perf_counter() - time_0))
    """
    02.10 20:10 - TIME key_bord() = 0.5482659560002503  == ping api.telegram.org  # OMG!
    """


def go_go_bot():
    print("telega.go_go_bot()")

    bot = TelegramBot.objects.get(in_work=True)
    print('bot_name: %s' % bot.name)

    updater = Updater(token=bot.token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    # echo_handler = MessageHandler(Filters.text, echo)
    get_coords = MessageHandler(Filters.location, coords)
    ask_help = MessageHandler(Filters.text, key_bord)

    dispatcher.add_handler(start_handler)
    # dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(get_coords)
    dispatcher.add_handler(ask_help)

    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    updater.start_polling()


if __name__ == "__main__":
    print('telega __main__')
    go_go_bot()

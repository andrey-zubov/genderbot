import logging

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from .models import TelegramBot


def sey_hello(bot, update):
    update.message.reply_text(
        "Hello %s" % update.message.from_user.first_name
    )


def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!"
    )


def echo(update, context):
    print("chat_id: %s" % update.message.chat_id)
    print("in_message: %s" % update.message.text)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text
    )


def coords(update, context):
    lat = float(update.message.location.latitude)
    lng = float(update.message.location.longitude)
    print("coord: %s, %s" % (lat, lng))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="lat: %s, lng: %s" % (lat, lng)
    )


def key_bord(update, context):
    key_bord_btn = [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]]
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Do you need Help?",

        reply_markup=ReplyKeyboardMarkup(key_bord_btn, one_time_keyboard=True)
    )


def go_go_bot():
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

# if __name__ == "__main__":
#     go_go_bot()

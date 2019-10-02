import logging
import os
from time import perf_counter
import django
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()


def sey_hello(bot, update):
    print("chat_id: %s" % update.message.chat_id)
    print("in_message: %s" % update.message.text)

    update.message.reply_text(
        "Hello %s" % update.message.from_user.first_name
    )


def start(update, context):
    print("telega.start(); chat_id: %s\nin_message: %s" % (update.message.chat_id, update.message.text))

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!"
    )


def echo(update, context):
    print("telega.echo(); chat_id: %s\nin_message: %s" % (update.message.chat_id, update.message.text))

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text
    )


def coords(update, context):
    print("telega.coords(); chat_id: %s\nin_message: %s" % (update.message.chat_id, update.message.text))

    lat = float(update.message.location.latitude)
    lng = float(update.message.location.longitude)
    print("coord: %s, %s" % (lat, lng))

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="lat: %s, lng: %s" % (lat, lng)
    )


def key_bord(update, context):
    time_0 = perf_counter()
    c_id = update.message.chat_id
    massage = update.message.text
    print("telega.key_bord(); chat_id: %s\nin_message: %s" % (c_id, massage))

    buttons = None
    if massage:
        from help_bot.models import NeedHelp
        root_nodes = NeedHelp.objects.root_nodes()
        root_nodes_names = [i.name for i in root_nodes]

        """ [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
        root_kb = [[KeyboardButton(text=i)] for i in root_nodes_names]
        buttons = root_kb

        if massage in root_nodes_names:
            children = root_nodes.get(name=massage).get_children()
            if children:
                children_names = [i.name for i in children]
                children_kb = [[KeyboardButton(text=i)] for i in children_names]
                buttons = children_kb
            else:
                print("No Children in the root: %s" % massage)

    key_bord_btn = buttons
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Do you need Help?",
        reply_markup=ReplyKeyboardMarkup(key_bord_btn, one_time_keyboard=True)
    )

    print("TIME - key_bord = %s" % (perf_counter() - time_0))


def go_go_bot():
    print("telega.go_go_bot()")

    from help_bot.models import TelegramBot
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

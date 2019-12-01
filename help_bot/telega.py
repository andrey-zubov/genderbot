import os
import sys
from time import sleep

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
from help_bot.loger_set_up import logger_telegram
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


@send_action(ChatAction.TYPING)
def start(update, context):
    _chat_id = update.message.chat_id

    try:
        key_bord_btn, help_text = keyboard_button(update.message.text, _chat_id)
    except Exception as ex:
        logger_telegram().exception("Exception TelegramBot.start().\n%s" % ex)
    else:
        try:
            context.bot.send_message(
                chat_id=_chat_id,
                text=help_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=ReplyKeyboardMarkup(key_bord_btn, resize_keyboard=True),
            )
        except Exception as ex:
            logger_telegram().exception("Exception TelegramBot.start().\n%s" % ex)


@send_action(ChatAction.TYPING)
def key_bord(update, context):
    _chat_id = update.message.chat_id

    try:
        key_bord_btn, help_text = keyboard_button(update.message.text, _chat_id)
    except Exception as ex:
        logger_telegram().exception("Exception TelegramBot.key_bord().\n%s" % ex)
    else:
        try:
            context.bot.send_message(
                chat_id=_chat_id,
                text=help_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=ReplyKeyboardMarkup(key_bord_btn, resize_keyboard=True),
            )
        except Exception as ex:
            logger_telegram().exception("Exception TelegramBot.key_bord().\n%s" % ex)


def go_go_bot(_logger) -> bool:
    start_telegram_bot = False
    try:
        bot_filter = TelegramBot.objects.filter(in_work=True)
        if len(bot_filter) > 1:
            raise Exception("More than 2 ACTIVE TelegramBot was found! %s" % [i for i in bot_filter],
                            start_telegram_bot)
        elif any(bot_filter):
            bot = bot_filter.first()
            print('TelegramBot name: %s' % bot.name)
        else:
            raise Exception("Active TelegramBot not found!", start_telegram_bot)
    except Exception as ex:
        _logger.exception("Exception in TelegramBot:\n%s" % ex.args[0])
        return ex.args[1]
    else:
        try:
            get_bot_token = bot.token
            if get_bot_token:
                bot_token = get_bot_token
                print('TelegramBot token - OK')
                start_telegram_bot = True
            else:
                start_telegram_bot = False
                raise Exception("TelegramBot token NOT set!", start_telegram_bot)
        except Exception as ex:
            _logger.exception("Exception in TelegramBot:\n%s" % ex.args[0])
            return ex.args[1]
        else:
            try:
                start_telegram_bot = True
                updater = Updater(token=bot_token, use_context=True)
                dispatcher = updater.dispatcher

                start_handler = CommandHandler('start', start)
                ask_help = MessageHandler(Filters.text, key_bord)

                dispatcher.add_handler(start_handler)
                dispatcher.add_handler(ask_help)

                updater.start_polling()

            except Exception as ex:
                _logger.exception("Exception in TelegramBot token:\n%s" % ex)

    return start_telegram_bot


if __name__ == "__main__":

    __my_logger = logger_telegram()
    __restart_bot_in_sec = 10

    print("Let's try to start telegram bot...")
    is_telegram_bot_running = False

    while not is_telegram_bot_running:
        is_telegram_bot_running = go_go_bot(__my_logger)
        if not is_telegram_bot_running:
            print('\tTelegramBot will restart in %s sec.' % __restart_bot_in_sec)
            sleep(__restart_bot_in_sec)

    print("! All OK, Telegram bot STARTed !\n")

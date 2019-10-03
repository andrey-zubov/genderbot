import logging
import os
from time import perf_counter

import django
from telegram import KeyboardButton

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import (NeedHelp, HelpText, StartMessage, ChatPosition)


def keyboard_button(_massage, _chat_id):
    if _massage:
        time_0 = perf_counter()
        print("_massage: %s" % _massage)

        user_position = 0
        user = None
        try:
            """ If user has ever used HelpBot -> find _chat_id id DB and get user last position, 
            else set user_position = 0. """
            users = ChatPosition.objects.all()
            for u in users.values():
                if u['chat_id'] == _chat_id:
                    user = ChatPosition.objects.get(chat_id=_chat_id)
                    user_position = user.user_chat_position
                    print("user_chat_position: %s" % user_position)
                    break
                else:
                    user_position = 0
                    print("user_position: %s" % user_position)
        except Exception as ex:
            logging.error("Exception in keyboard_button().user_position\n%s" % ex)

        if user and not user_position:
            """ user came from a start questions """
            print("user.id: %s" % user.id)
            root_nodes = NeedHelp.objects.root_nodes()
            for r in root_nodes:
                if _massage == r.user_input:
                    user_position = r.id
                    children = r.get_children()
                    btn_text = [i.user_input for i in children]
                    print("btn_text: %s" % btn_text)

                    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]
                    text = HelpText.objects.get(relation_to=user_position).text
                    print("text: %s" % text)

                    """ TBA """
                    print("Save user position: %s" % user_position)
                    chat = ChatPosition.objects.get(chat_id=_chat_id)
                    chat.user_chat_position = user_position
                    chat.save()

                    print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
                    return btn_to_send, text
            else:
                print("_massage not in root_nodes.user_input")
                return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")

        if user_position:
            """ user used HelpBot and have last saved position """
            print("user_has_position: %s" % user_position)

            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")

        else:
            """ From user input: /start, random input """
            print("else")

            if not user:
                """ Save User """
                print("Save User: _chat_id = %s, user_position = %s" % (_chat_id, user_position))
                ChatPosition(chat_id=_chat_id, user_chat_position=user_position).save()

            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return default_output(_chat_id, us_pos=user_position)

    else:
        print("No _massage keyboard_button()")
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            level=logging.INFO)
        return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")


def default_output(ch_id, us_pos=0, sorry=''):
    print("default_output()")
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes]
    # print("btn_text: %s" % btn_text)
    """ [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]

    text = StartMessage.objects.get().text
    # print("text: %s" % text)

    """ Save user position or Reset to 0"""
    if us_pos == 0:
        print("Reset user position to 0")
    else:
        print("Save user position: %s" % us_pos)
    chat = ChatPosition.objects.get(chat_id=ch_id)
    chat.user_chat_position = us_pos
    chat.save()

    """ sorry = error massage to the user. """
    return btn_to_send, "%s%s" % (sorry, text)


"""
02.10 20:10 - TIME keyboard_button() = 0.005887855993933044
"""

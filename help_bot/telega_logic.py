import logging
import os
from time import perf_counter

import django
from telegram import KeyboardButton

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import (NeedHelp, HelpText, StartMessage, ChatPositionTelegram)


def keyboard_button(_massage, _chat_id):
    if _massage:
        time_0 = perf_counter()
        print("_massage: %s" % _massage)

        user_position = 0
        user = None
        try:
            """ If user has ever used HelpBot -> find _chat_id id DB and get user last position, 
            else set user_position = 0. """
            users = ChatPositionTelegram.objects.all()
            for u in users.values():
                if u['chat_id'] == _chat_id:
                    user = ChatPositionTelegram.objects.get(chat_id=_chat_id)
                    user_position = user.position
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

                    save_user_pos(_chat_id, user_position, True)

                    print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
                    return btn_and_text(children, user_position)
            else:
                print("_massage not in root_nodes.user_input")
                return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")

        elif user_position:
            """ user used HelpBot and have last saved position """
            print("user_has_position: %s" % user_position)

            child = NeedHelp.objects.get(id=user_position).get_children()
            for c in child:
                if _massage == c.user_input:

                    if c.link_to:
                        """ If this button has a link to the other help option. Select list in Admin. """
                        print("link_to: %s" % c.link_to.id)
                        user_position = c.link_to.id
                        ch_ch = NeedHelp.objects.get(id=user_position).get_children()

                    elif c.go_back:
                        """ Back to the main questions. Check_box in Admin. """
                        return default_output(_chat_id)

                    else:
                        """ Normal buttons in the chat. Go deeper. """
                        user_position = c.id
                        ch_ch = c.get_children()

                    save_user_pos(_chat_id, user_position, True)

                    print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
                    return btn_and_text(ch_ch, user_position)
            else:
                print("_massage not in child.user_input")
                return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")

        else:
            """ From user input: /start, random input """
            print("else")
            if not user:
                """ Save/remember the User """
                save_user_pos(_chat_id, user_position, None)
            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return default_output(_chat_id, us_pos=user_position)

    else:
        print("No _massage keyboard_button()")
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            level=logging.INFO)
        return default_output(_chat_id, sorry="Извените, произошла ошибка!\n\n")


def default_output(ch_id: int, us_pos=0, sorry=''):
    """ Reset user position to the Start Questions menu. """
    print("default_output()")
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes]
    # print("btn_text: %s" % btn_text)
    """ [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]

    text = StartMessage.objects.get().text
    # print("text: %s" % text)

    save_user_pos(ch_id, us_pos, True)

    """ sorry = error massage to the user. """
    return btn_to_send, "%s%s" % (sorry, text)


def btn_and_text(child, us_pos: int):
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    btn_text = [i.user_input for i in child]
    print("btn_text: %s" % btn_text)
    btn = [[KeyboardButton(text=i)] for i in btn_text]

    # text = HelpText.objects.get(relation_to=us_pos).text
    # print("text: %s" % text)
    text = None
    text_obj = HelpText.objects.get(relation_to=us_pos)
    if text_obj:
        text = text_obj.text
    # ht_obj = NeedHelp.objects.get(id=us_pos).select_help_text
    # if not text and ht_obj:
    #     text = ht_obj.text
    print("text: %s" % text)

    return btn, text


def save_user_pos(_chat_id: int, _us_pos: int, _user=None):
    """ TBA """
    print("save_user_pos(); ip: %s, us_pos: %s, user: %s" % (_chat_id, _us_pos, _user))
    if _user:
        chat = ChatPositionTelegram.objects.get(chat_id=_chat_id)
        chat.position = _us_pos
        chat.save()
    else:
        ChatPositionTelegram(chat_id=_chat_id, position=_us_pos).save()


"""
02.10 20:10 - TIME keyboard_button() = 0.005887855993933044
"""

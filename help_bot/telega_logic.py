import logging
from time import perf_counter

from telegram import KeyboardButton

from help_bot.models import (NeedHelp, HelpText, StartMessage, ChatPositionTelegram, StatisticTelegram)


def keyboard_button(_massage: str, _chat_id: int) -> (list, str):
    print("keyboard_button()")
    if _massage:
        time_0 = perf_counter()
        print("_massage: %s" % _massage)
        user, user_position = find_telegram_user(_chat_id)

        if user and not user_position:
            """ user came from a start questions """
            s_text = user_from_start(_chat_id, _massage)
            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return s_text
        elif user_position:
            """ user used HelpBot and have last saved position """
            q_text = known_user(_chat_id, user_position, _massage)
            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return q_text
        else:
            """ From user input: /start, random input """
            rand = random_input(_chat_id, True)
            print("TIME keyboard_button() = %s\n" % (perf_counter() - time_0))
            return rand

    else:
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            level=logging.INFO)
        return default_output()


def find_telegram_user(_chat_id: int) -> (bool, int):
    """ If user has ever used HelpBot -> find chat_id id DB and get user last position,
    else set user_position = 0. """
    print("find_telegram_user()")
    try:
        users_all = ChatPositionTelegram.objects.all().values()
        for u in users_all:
            if u['chat_id'] == _chat_id:
                return True, u['position']
        save_telegram_user(_chat_id, 0, False)
        return True, 0
    except Exception as ex:
        logging.error("Exception in find_telegram_user()\n%s" % ex)
        return False, 0


def save_telegram_user(_chat_id: int, _us_pos: int, _user: bool):
    """ save user current position or create new user with default position = 0. """
    print("save_telegram_user(); chat_id: %s, us_pos: %s, user: %s" % (_chat_id, _us_pos, _user))
    if _user:
        chat = ChatPositionTelegram.objects.get(chat_id=_chat_id)
        chat.position = _us_pos
        chat.save()

        if _us_pos:
            st_web = StatisticTelegram.objects.get(id=_us_pos)
            st_web.count += 1
            st_web.save()
    else:
        ChatPositionTelegram(chat_id=_chat_id, position=_us_pos).save()


def default_output() -> (list, str):
    """ Reset user position to the Start Questions menu. """
    print("default_output()")
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    """ Telegram buttons: [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]
    # print("btn_text: %s" % btn_text)
    text = StartMessage.objects.get(default=True).text
    # print("text: %s" % text)
    return btn_to_send, text


def btn_and_text(child, us_pos: int) -> (list, str):
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    print("btn_and_text()")
    btn_text = [i.user_input for i in child]
    btn = [[KeyboardButton(text=i)] for i in btn_text]
    # print("btn_text: %s" % btn_text)
    text = HelpText.objects.get(relation_to=us_pos).text
    # print("text: %s" % text)
    return btn, text


def user_from_start(_chat_id: int, _massage: str) -> (list, str):
    """ user came from a start questions """
    print("user_from_start()")
    root_nodes = NeedHelp.objects.root_nodes()
    for r in root_nodes:
        if _massage == r.user_input:
            user_position = r.id
            children = r.get_children()
            save_telegram_user(_chat_id, user_position, True)
            return btn_and_text(children, user_position)
    return random_input(_chat_id, True)


def known_user(_chat_id: int, _user_position: int, _massage: str) -> (list, str):
    """ user used HelpBot and have last saved position """
    print("known_user()")
    root = NeedHelp.objects.get(id=_user_position)
    child = root.get_children()
    if child:
        for c in child:
            if _massage == c.user_input:
                if c.link_to:
                    """ If this button has a link to the other help option. Select list in Admin. """
                    user_position = c.link_to.id
                    new_child = NeedHelp.objects.get(id=user_position).get_children()
                elif c.go_back:
                    """ Back to the main questions. Check_box in Admin. """
                    save_telegram_user(_chat_id, 0, True)
                    return default_output()
                elif c.go_default:
                    """ if user clicked last element of the Tree - go to default branch. """
                    user_position = c.id
                    new_child = NeedHelp.objects.get(is_default=True).get_children()
                else:
                    """ Normal buttons in the chat. Go deeper. """
                    user_position = c.id
                    new_child = c.get_children()

                save_telegram_user(_chat_id, user_position, True)
                return btn_and_text(new_child, user_position)
        return random_input(_chat_id, True)

    elif root.go_default:
        """ if user at the last element of the Tree - go to default branch.
        is_default=True - hidden root node for a default output that repeats at last tree element. """
        print("root.go_default")
        new_root = NeedHelp.objects.get(is_default=True)
        new_child = new_root.get_children()
        for c in new_child:
            if _massage == c.user_input:
                if c.go_back:
                    save_telegram_user(_chat_id, 0, True)
                    return default_output()
                else:
                    return known_user(_chat_id, new_root.id, _massage)

    return random_input(_chat_id, True)


def random_input(_chat_id: int, _user: bool) -> (list, str):
    """ Reset user position to the Start Questions menu. """
    print("random_input()")
    save_telegram_user(_chat_id, 0, _user)
    return default_output()


"""
02.10 20:10 - TIME keyboard_button() = 0.005887855993933044
"""

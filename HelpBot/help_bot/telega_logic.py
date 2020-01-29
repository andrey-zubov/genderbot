from telegram import KeyboardButton

from help_bot.loger_set_up import logger_telegram
from help_bot.models import (NeedHelp, HelpText, StartMessage, ChatPositionTelegram, EditionButtons)
from help_bot.statistic import (save_telegram_chat_statistic)
from help_bot.utility import try_except


def keyboard_button(_massage: str, _chat_id: int) -> (list, str):
    """ Telegram chat bot main logic. """
    if len(_massage) > 1:
        # print("_massage: %s" % _massage)
        user, user_position = find_telegram_user(_chat_id)

        if user and not user_position:
            """ user came from a start questions + /start """
            return user_from_start(_chat_id, _massage)

        elif user_position:
            """ user used HelpBot and have last saved position """
            return known_user(_chat_id, user_position, _massage)

        else:
            """ random input """
            return random_input(_chat_id, True, sorry=True)
    else:
        logger_telegram().warning("Error in keyboard_button(), len(_massage) < 1")
        return default_output(sorry=True)


def find_telegram_user(_chat_id: int) -> (bool, int):
    """ If user has ever used HelpBot -> find chat_id id DB and get user last position,
    else set user_position = 0. """
    try:
        users_all = ChatPositionTelegram.objects.all().values()
        for u in users_all:
            if u['chat_id'] == _chat_id:
                return True, u['position']
        save_telegram_user(_chat_id, 0, False)
        return True, 0
    except Exception as ex:
        logger_telegram().error("Exception in find_telegram_user()\n%s" % ex)
        return False, 0


@try_except
def save_telegram_user(_chat_id: int, _us_pos: int, _user: bool):
    """ save user current position or create new user with default position = 0. """
    if _user:
        chat = ChatPositionTelegram.objects.get(chat_id=_chat_id)
        chat.position = _us_pos
        chat.save()

        if _us_pos:
            save_telegram_chat_statistic(_us_pos)
    else:
        cp = ChatPositionTelegram(chat_id=_chat_id, position=_us_pos)
        cp.save()


def default_output(sorry=False, help_type=False) -> (list, str):
    """ Reset user position to the Start Questions menu. """
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    """ Telegram buttons: [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]

    if help_type:
        text_ht = help_type_text_msg()
        text_out = text_ht if text_ht else start_msg_text()
    elif sorry:
        text_out = "%s\n\n%s" % (sorry_text_msg(), help_type_text_msg())
    else:
        text_out = start_msg_text()

    return btn_to_send, text_out


def start_msg_text() -> str:
    try:
        text_h = StartMessage.objects.filter(hello_text=True)
        if text_h:
            return text_h.first().text
        logger_telegram().error("Стартовое сообщение приветствия отсутствует!")
        return ''
    except Exception as ex:
        logger_telegram().exception("Exception in start_msg_text()\n%s" % ex)
        return ''


def sorry_text_msg() -> str:
    """ Sorry text if wrong input. Adding to the TOP of the "Hello" text. """
    try:
        text_obj = StartMessage.objects.filter(sorry_text=True)
        if any(text_obj):
            return text_obj.first().text
        logger_telegram().error("Сообщение об ошибке ввода отсутствует!")
        return ''
    except Exception as ex:
        logger_telegram().exception("Exception in sorry_text_msg()\n%s" % ex)
        return ''


def help_type_text_msg() -> str:
    """ костыль, чтобы сообщение приветствия не повторялось при возврате к стартовым вопросам.
        "help_type" - название специального сообщения в разделе "Стартовое сообщение бота".
    """
    try:
        text_obj = StartMessage.objects.filter(name='help_type')
        if text_obj:
            return text_obj.first().text
        logger_telegram().error("Альтернативное сообщение при возврате к стартовым вопросам отсутствует!")
        return ''
    except Exception as ex:
        logger_telegram().exception("Exception in help_type_text_msg()\n%s" % ex)
        return ''


def btn_and_text(child, us_pos: int) -> (list, str):
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    btn_text_list = []

    normal_chat_buttons = [i.user_input for i in child]

    start_btn = additional_start_btn()
    if start_btn and start_btn not in normal_chat_buttons:
        btn_text_list.extend([start_btn])

    btn_text_list.extend(normal_chat_buttons)

    buttons_out = [[KeyboardButton(text=i)] for i in btn_text_list]

    text_out = ''
    for t in HelpText.objects.filter(relation_to=us_pos):
        if t:
            try:
                text_out += t.text
                if t.telegram_geo_url and t.address:
                    text_out += """\n<a href="{}">{}</a>\n\n""".format(t.telegram_geo_url, t.address)
            except Exception as ex:
                logger_telegram().error("Exception in btn_and_text():\n%s" % ex)
                continue
        else:
            continue

    return buttons_out, text_out


def additional_start_btn():
    try:
        active_buttons = EditionButtons.objects.get(btn_active=True, btn_position_start=True)
        return active_buttons.btn_name
    except Exception as ex:
        logger_telegram().exception("Exception in additional_start_btn()\n%s" % ex)
        return None


def user_from_start(_chat_id: int, _massage: str) -> (list, str):
    """ user came from a start questions """
    root_nodes = NeedHelp.objects.root_nodes()
    for r in root_nodes:
        if _massage == r.user_input:
            user_position = r.id
            children = r.get_children()
            save_telegram_user(_chat_id, user_position, True)
            return btn_and_text(children, user_position)

    if _massage == "/start":
        return random_input(_chat_id, True, sorry=False)
    else:
        return random_input(_chat_id, True, sorry=True)


def known_user(_chat_id: int, _user_position: int, _massage: str) -> (list, str):
    """ user used HelpBot and have last saved position """
    root = NeedHelp.objects.get(id=_user_position)
    child = root.get_children()
    if child:
        for c in child:
            if _massage == c.user_input:
                if c.link_to:
                    """ If this button has a link to the other help option. Select list in Admin. """
                    user_position = c.link_to.id
                    new_child = NeedHelp.objects.get(id=user_position).get_children()
                    if not new_child:
                        new_child = NeedHelp.objects.get(is_default=True).get_children()
                elif c.go_back:
                    """ Back to the main questions. Check_box in Admin. """
                    save_telegram_user(_chat_id, 0, True)
                    return default_output(help_type=True)
                elif c.go_default:
                    """ if user clicked last element of the Tree - go to default branch. """
                    user_position = c.id
                    try:
                        new_child = NeedHelp.objects.get(is_default=True).get_children()
                    except Exception as ex:
                        logger_telegram().exception("Chat Tree DO NOT have element with is_default=True!\n%s" % ex)
                        return random_input(_chat_id, True, sorry=True)
                else:
                    """ Normal buttons in the chat. Go deeper. """
                    user_position = c.id
                    new_child = c.get_children()

                save_telegram_user(_chat_id, user_position, True)
                return btn_and_text(new_child, user_position)
        """ button text not in the list. """
        return random_input(_chat_id, True, sorry=True)

    elif root.go_default:
        """ if user at the last element of the Tree - go to default branch.
        is_default=True - hidden root node for a default output that repeats at last tree element. """
        try:
            new_root = NeedHelp.objects.get(is_default=True)
        except Exception as ex:
            logger_telegram().exception("Chat Tree DO NOT have element with is_default=True!\n%s" % ex)
            return random_input(_chat_id, True, sorry=True)
        new_child = new_root.get_children()
        for c in new_child:
            if _massage == c.user_input:
                if c.go_back:
                    save_telegram_user(_chat_id, 0, True)
                    return default_output(help_type=True)
                else:
                    return known_user(_chat_id, new_root.id, _massage)

    return random_input(_chat_id, True, sorry=True)


def random_input(_chat_id: int, _user: bool, sorry=False) -> (list, str):
    """ Reset user position to the Start Questions menu. """
    save_telegram_user(_chat_id, 0, _user)
    return default_output(sorry=sorry)

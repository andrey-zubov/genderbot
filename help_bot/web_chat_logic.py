import json
import logging
from time import perf_counter

from help_bot.models import (NeedHelp, StartMessage, ChatPositionWeb, HelpText, StatisticWeb)


def chat_req_get(request) -> str:
    """ TBA """
    time_0 = perf_counter()
    if any(request.GET.values()):
        ui = request.GET['us_in'].strip()
        # print("user_input: %s" % ui)
        ip = get_client_ip(request)
        user, user_position = find_web_user(ip)
        StatisticWeb(id=user_position)

        if check_input(ui):
            if user and not user_position:
                """ user came from a start questions """
                send_text = user_from_start_q(ui, ip)
                print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
                return send_text
            elif user_position:
                """ user used HelpBot and have last saved position """
                send_text = user_has_position(ip, user_position, ui)
                print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
                return send_text
        else:
            """ random input from a user """
            st = random_input(ip, user)
            print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
            return st
    else:
        logging.error("request.GET is empty!")
        return start_chat()


def start_chat() -> str:
    """ Start Questions menu. """
    print("start_chat()")
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    print("btn_text: %s" % btn_text)
    text = StartMessage.objects.get(default=True).text.replace("\n", "<br>")
    json_data = json.dumps({'btn_text': btn_text, "help_text": text}, ensure_ascii=False)
    # print("json: %s" % json_data)
    return json_data


def find_web_user(_ip: str) -> (bool, int):
    """ If user has ever used HelpBot -> find chat_id id DB and get user last position.
    Else set user_position = 0. """
    print("find_web_user()")
    try:
        chat_web_all = ChatPositionWeb.objects.all().values()
        for w in chat_web_all:
            if w['ip_address'] == _ip:
                return True, w['position']
        save_web_user(_ip, 0, False)
        return True, 0
    except Exception as ex:
        logging.error("Exception in find_web_user()\n%s" % ex)
        return False, 0


def save_web_user(_ip: str, _user_position: int, _user: bool):
    """ save user current position or create new user with default position = 0. """
    print("save_web_user(); ip: %s, us_pos: %s, user: %s" % (_ip, _user_position, _user))
    if _user:
        web_chat = ChatPositionWeb.objects.get(ip_address=_ip)
        web_chat.position = _user_position
        web_chat.save()

        if _user_position:
            st_web = NeedHelp.objects.get(id=_user_position).statistic_web
            # st_web = StatisticWeb.objects.get(id=_user_position)
            st_web.count += 1
            st_web.save()
    else:
        ChatPositionWeb(ip_address=_ip, position=_user_position).save()


def user_from_start_q(_massage: str, ip: str) -> str:
    """ user came from a start questions """
    print("user_from_start_q()")
    root_node = NeedHelp.objects.root_nodes()
    for r in root_node:
        if _massage == r.user_input:
            user_position = r.id
            children = r.get_children()
            save_web_user(ip, user_position, True)
            return buttons_and_text(children, user_position)
    return random_input(ip, True)


def user_has_position(_ip: str, _user_position: int, _massage: str) -> str:
    """ user used HelpBot and have last saved position """
    print("user_has_position()")
    root = NeedHelp.objects.get(id=_user_position)
    child = root.get_children()
    if child:
        """ normal tree branch """
        for c in child:
            if _massage == c.user_input:
                if c.link_to:
                    """ If this button has a link to the other help option. Select_list in the Admin menu. """
                    user_position = c.link_to.id
                    new_child = NeedHelp.objects.get(id=user_position).get_children()
                elif c.go_back:
                    """ Back to the main questions. Check_box in the Admin menu. """
                    save_web_user(_ip, 0, True)
                    return start_chat()
                elif c.go_default:
                    """ if user clicked last element of the Tree - go to default branch. """
                    user_position = c.id
                    new_child = NeedHelp.objects.get(is_default=True).get_children()
                else:  # How to speed up: add new field -> normal_element = models.BooleanField,
                    """ Normal buttons in the chat. Go deeper. """  # but it'l be to hard for Admin ?!
                    user_position = c.id
                    new_child = c.get_children()

                save_web_user(_ip, user_position, True)
                return buttons_and_text(new_child, user_position)
        return random_input(_ip, True)

    elif root.go_default:
        """ if user at the last element of the Tree - go to default branch. """
        return go_default_branch(_ip, _massage)

    return random_input(_ip, True)


def go_default_branch(_ip: str, _massage: str) -> str:
    """ is_default=True - hidden root node for a default output that repeats at last tree elements. """
    print("go_default_branch()")
    new_root = NeedHelp.objects.get(is_default=True)
    new_child = new_root.get_children()
    for c in new_child:
        if _massage == c.user_input:
            if c.go_back:
                """ Back to the main questions. Check_box in the Admin menu. """
                save_web_user(_ip, 0, True)
                return start_chat()
            else:
                return user_has_position(_ip, new_root.id, _massage)
    return random_input(_ip, True)


def random_input(_ip: str, _user: bool) -> str:
    """ Reset user position to the Start Questions menu. """
    print("random_input()")
    save_web_user(_ip, 0, _user)
    return start_chat()


def buttons_and_text(_child, _user_position: int) -> str:
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    print("buttons_and_text()")
    btn_text = [i.user_input for i in _child]
    # print("btn_text: %s" % btn_text)
    text = HelpText.objects.get(relation_to=_user_position).text.replace("\n", "<br>")
    # text  # TODO: url -> <a>
    # print("text: %s" % text)
    json_data = json.dumps({'btn_text': btn_text, "help_text": text}, ensure_ascii=False)
    return json_data


def check_input(string: str) -> bool:
    """ Do i need to check all inputs?! Usability for others?! """
    s = string.replace(" ", "")
    if s.isalpha():
        return True
    return False


def get_client_ip(request) -> str:
    print("get_client_ip()")
    # print("request.META: %s" % request.META)
    # print("User.HTTP_COOKIE: %s" % request.META.get('HTTP_COOKIE'))
    # 'HTTP_COOKIE': 'lastpath="http://127.0.0.1:8000/log/login/";
    # print("User.REMOTE_ADDR: %s" % request.META.get('REMOTE_ADDR'))
    # 'REMOTE_ADDR': '192.168.0.51'
    # print("User.HTTP_HOST: %s" % request.META.get('HTTP_HOST'))
    # 'HTTP_HOST': '192.168.0.51:8000'
    # print("User.HTTP_REFERER: %s" % request.META.get('HTTP_REFERER'))
    # 'HTTP_REFERER': 'http://192.168.0.51:8000/'
    # print("User.HTTP_COOKIE: %s" % request.META.get('HTTP_COOKIE'))
    # 'HTTP_COOKIE': 'csrftoken=FD0o027YvhJ6eogKBVQFDMerWC8dM9uiNRmL2KVopbCs8z8ZUQukBIPE65Zsmdsz'
    # print("User.CSRF_COOKIE: %s" % request.META.get('CSRF_COOKIE'))
    # 'CSRF_COOKIE': 'FD0o027YvhJ6eogKBVQFDMerWC8dM9uiNRmL2KVopbCs8z8ZUQukBIPE65Zsmdsz'
    # print("User.USERNAME: %s" % request.META.get('USERNAME'))
    # 'USERNAME': 'bequite'
    # print("User.USER: %s" % request.META.get('USER'))
    # 'USER': 'bequite'
    # 'SERVER_NAME': 'server.Dlink'
    # 'PATH_INFO': '/chat_test/'

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    print('User.IP: %s' % ip)
    return ip

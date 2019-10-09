import json
import logging
from time import perf_counter

from help_bot.models import (NeedHelp, StartMessage, ChatPositionWeb, HelpText)


def chat_req_get(request):
    """ TBA """
    time_0 = perf_counter()
    if any(request.GET.values()):
        ui = str(request.GET['us_in']).strip()
        print("user_input: %s" % ui)

        ip = get_client_ip(request)
        user, user_position = find_web_user(ip)

        if check_input(ui):
            # if ui == "Связаться с консультантом":
            #     return start_chat()
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
            random_input(ip, user)
            print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
            return start_chat()
    else:
        logging.error("request.GET is empty!")
        return start_chat()


def start_chat() -> str:
    """ Start Questions menu. """
    print("start_chat()")
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    print("btn_text: %s" % btn_text)
    # """ easy way to RegExp Array in FrontEnd. """
    # btn = '|'.join(btn_text)
    text = StartMessage.objects.get(default=True).text

    json_data = json.dumps({'btn_text': btn_text, "help_text": text}, ensure_ascii=False)
    # print("json: %s" % json_data)

    # """ easy way to RegExp Array of the buttons and Help Text in FrontEnd. """
    # return "%s#####%s" % (btn, text)
    return json_data


def find_web_user(_ip: str) -> (bool, int):
    print("find_web_user(); ip: %s" % _ip)
    try:
        chat_web_all = ChatPositionWeb.objects.all().values()
        for w in chat_web_all:
            if w['ip_address'] == _ip:
                return True, int(w['position'])
        save_web_user(_ip, 0, False)  # create new user, default position = 0
        return True, 0  # (user, user_position)
    except Exception as ex:
        logging.error("Exception in find_web_user()\n%s" % ex)
        return False, 0  # (user, user_position)


def save_web_user(_ip: str, _user_position: int, _user: bool):
    print("save_web_user(); ip: %s, us_pos: %s, user: %s" % (_ip, _user_position, _user))
    if _user:
        web_chat = ChatPositionWeb.objects.get(ip_address=_ip)
        web_chat.position = _user_position
        web_chat.save()
    else:
        ChatPositionWeb(ip_address=_ip, position=_user_position).save()


def user_from_start_q(_massage: str, ip: str):
    """ user came from a start questions """
    print("user_from_start_q(); m: %s; ip: %s" % (_massage, ip))
    root_node = NeedHelp.objects.root_nodes()
    for r in root_node:
        if _massage == r.user_input:
            user_position = r.id
            children = r.get_children()
            save_web_user(ip, user_position, True)
            return buttons_and_text(children, user_position)
    print("Massage not in root_nodes.user_input")
    save_web_user(ip, 0, True)
    return start_chat()


def user_has_position(_ip, _user_position, _massage):
    """ user used HelpBot and have last saved position """
    print("user_has_position(); ip: %s, us_pos: %s" % (_ip, _user_position))
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
                else:
                    """ Normal buttons in the chat. Go deeper. """
                    user_position = c.id
                    new_child = c.get_children()

                save_web_user(_ip, user_position, True)
                return buttons_and_text(new_child, user_position)
    elif root.go_default:
        """ if user at the last element of the Tree - go to default branch.
        is_default=True - hidden root node for a default output that repeats at last tree element. """
        print("root.go_default")
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
        # new_user_position = new_root.id
        # user_has_position(_ip, new_user_position, _massage)
        # save_web_user(_ip, new_user_position, True)
        # new_child = new_root.get_children()
        # return buttons_and_text(new_child, new_user_position)

    print("Massage not in root_nodes.user_input")
    save_web_user(_ip, 0, True)
    return start_chat()


def random_input(_ip, _user):
    """ Reset user position to the Start Questions menu. """
    print("random_input()")
    save_web_user(_ip, 0, _user)
    return start_chat()


def buttons_and_text(_child, _user_position: int) -> str:
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    print("buttons_and_text(); user_position: %s" % _user_position)
    btn_text = [i.user_input for i in _child]  # if i.show_ui
    print("btn_text: %s" % btn_text)
    # """ easy way to RegExp Array in FrontEnd. """
    # btn = '|'.join(btn_text)

    text = None
    text_obj = HelpText.objects.get(relation_to=_user_position)
    if text_obj:
        text = text_obj.text
    # ht_obj = NeedHelp.objects.get(id=_user_position).select_help_text
    # if not text and ht_obj:
    #     text = ht_obj.text
    print("text: %s" % text)
    json_data = json.dumps({'btn_text': btn_text, "help_text": text}, ensure_ascii=False)
    # print("json: %s" % json_data)
    # """ easy way to RegExp Array of the buttons and Help Text in FrontEnd. """
    # return "%s#####%s" % (btn, text)
    return json_data


def check_input(string: str) -> bool:
    """ Do i need to check all inputs?! Usability for others?! """
    s = string.replace(" ", "")
    if s.isalpha():
        return True
    return False


def get_client_ip(request):
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

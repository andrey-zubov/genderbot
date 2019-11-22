import json
import logging

from help_bot.models import (NeedHelp, StartMessage, ChatPositionWeb, HelpText)
from help_bot.statistic import (save_web_chat_statistic)
from help_bot.utility import (check_input, try_except)


def chat_req_get(request) -> str:
    """ Web chat bot main logic. """
    if any(request.GET.values()):
        ui = request.GET['us_in'].strip()
        ip = get_client_ip(request)
        user, user_position = find_web_user(ip)

        if check_input(ui):
            if user and not user_position:
                """ user came from a start questions """
                return user_from_start_q(ui, ip)

            elif user_position:
                """ user used HelpBot and have last saved position """
                return user_has_position(ip, user_position, ui)
        else:
            """ random input from a user """
            return random_input(ip, user, sorry=True)
    else:
        """ Chat page load. """
        logger = logging.getLogger(__name__)
        logger.info("request.GET is empty.")
        return start_chat()


def start_chat(sorry=False, help_type=False) -> str:
    """ Start Questions menu. """
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]

    text_h = StartMessage.objects.filter(hello_text=True)
    if text_h:
        text_hello = text_h[0].text.replace("\n", "<br>")
    else:
        text_hello = ''

    if help_type:
        text_ht = StartMessage.objects.filter(name='help_type')
        if text_ht:
            text_out = text_ht.first().text
        else:
            text_out = text_hello
    elif sorry:
        text_s = StartMessage.objects.filter(sorry_text=True)
        if text_s:
            text_sorry = text_s[0].text.replace("\n", "<br>")
        else:
            text_sorry = ''

        text_out = "%s<br><br>%s" % (text_sorry, text_hello)
    else:
        text_out = text_hello

    return json.dumps({'btn_text': btn_text, "help_text": text_out}, ensure_ascii=False)


def find_web_user(_ip: str) -> (bool, int):
    """ If user has ever used HelpBot -> find chat_id id DB and get user last position.
    Else set user_position = 0. """
    try:
        for w in ChatPositionWeb.objects.all():
            if w.ip_address == _ip:
                return True, w.position
        save_web_user(_ip, 0, False)
        return True, 0
    except Exception as ex:
        logger = logging.getLogger(__name__)
        logger.exception("Exception in find_web_user()\n%s" % ex)
        return False, 0


@try_except
def save_web_user(_ip: str, _user_position: int, _user: bool):
    """ save user current position or create new user with default position = 0. """
    if _user:
        web_chat = ChatPositionWeb.objects.get(ip_address=_ip)
        web_chat.position = _user_position
        web_chat.save()

        if _user_position:
            save_web_chat_statistic(_user_position)
    else:
        cp = ChatPositionWeb(ip_address=_ip, position=_user_position)
        cp.save()


def user_from_start_q(_massage: str, ip: str) -> str:
    """ user came from a start questions """
    root_node = NeedHelp.objects.root_nodes()
    for r in root_node:
        if _massage == r.user_input:
            user_position = r.id
            children = r.get_children()
            save_web_user(ip, user_position, True)
            return buttons_and_text(children, user_position)
    return random_input(ip, True, sorry=True)


def user_has_position(_ip: str, _user_position: int, _massage: str) -> str:
    """ user used HelpBot and have last saved position """
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
                    if not new_child:
                        new_child = NeedHelp.objects.get(is_default=True).get_children()
                elif c.go_back:
                    """ Back to the main questions. Check_box in the Admin menu. """
                    save_web_user(_ip, 0, True)
                    return start_chat(help_type=True)
                elif c.go_default:
                    """ if user clicked last element of the Tree - go to default branch. """
                    user_position = c.id
                    try:
                        new_child = NeedHelp.objects.get(is_default=True).get_children()
                    except Exception as ex:
                        logging.exception("Chat Tree DO NOT have element with is_default=True!\n%s" % ex)
                        return random_input(_ip, True, sorry=True)
                else:  # How to speed up: add new field -> normal_element = models.BooleanField,
                    """ Normal buttons in the chat. Go deeper. """  # but it'l be to hard for Admin ?!
                    user_position = c.id
                    new_child = c.get_children()

                save_web_user(_ip, user_position, True)
                return buttons_and_text(new_child, user_position)
        return random_input(_ip, True, sorry=True)

    elif root.go_default:
        """ if user at the last element of the Tree - go to default branch. """
        return go_default_branch(_ip, _massage)

    return random_input(_ip, True, sorry=True)


def go_default_branch(_ip: str, _massage: str) -> str:
    """ is_default=True - hidden root node for a default output that repeats at last tree elements. """
    try:
        new_root = NeedHelp.objects.get(is_default=True)
    except Exception as ex:
        logging.exception("Chat Tree DO NOT have element with is_default=True!\n%s" % ex)
        return random_input(_ip, True, sorry=True)
    else:
        new_child = new_root.get_children()
        for c in new_child:
            if _massage == c.user_input:
                if c.go_back:
                    """ Back to the main questions. Check_box in the Admin menu. """
                    save_web_user(_ip, 0, True)
                    return start_chat(help_type=True)
                else:
                    return user_has_position(_ip, new_root.id, _massage)
        return random_input(_ip, True, sorry=True)


def random_input(_ip: str, _user: bool, sorry=False) -> str:
    """ Reset user position to the Start Questions menu. """
    save_web_user(_ip, 0, _user)
    return start_chat(sorry=sorry)


def buttons_and_text(_child, _user_position: int) -> str:
    """ Avery Tree Field in the Admin menu has 'User input' option.
    'User input' = text buttons, that must be send to the chat. """
    btn_text = [i.user_input for i in _child]

    text_sum = ''
    for t in HelpText.objects.filter(relation_to=_user_position):
        if t:
            try:
                text_sum += t.text.replace("\n", "<br>")
                text_sum += "<br>"
                if t.geo_link_name and t.address:
                    text_sum += get_geo_link_web(t.geo_link_name, t.address, t.latitude, t.longitude)
            except Exception as ex:
                logger = logging.getLogger(__name__)
                logger.exception("Exception in buttons_and_text():\n%s" % ex)
                continue
        else:
            continue

    json_data = json.dumps({'btn_text': btn_text, "help_text": text_sum}, ensure_ascii=False)
    return json_data


def get_geo_link_web(_link_name: str, _address: str, _lat: float, _lng: float) -> str:
    if _lat and _lng:
        """ data-bounds=[[55.729410, 37.584012], [55.738588, 37.598817]]
            Данный параметр рекомендуется указывать, если в геоссылке задан неполный адрес объекта, 
            например без указания города или области («ул. Ленина»). """
        delta_lat = 0.00415  # ~0.5 km
        delta_lng = 0.007  # ~0.5 km
        coords_square = [[_lat + delta_lat, _lng - delta_lng], [_lat - delta_lat, _lng + delta_lng]]
    else:
        coords_square = ''

    return """<p><span class="ymaps-geolink" data-type="biz" data-bounds="{}">{} {}</span></p><br>""".format(
        coords_square,
        _link_name,  # no <br> here between them!!!
        _address)


def get_client_ip(request) -> str:
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
    # print("User.SERVER_NAME: %s" % request.META.get('SERVER_NAME'))
    # 'SERVER_NAME': 'server.Dlink'
    # print("User.PATH_INFO: %s" % request.META.get('PATH_INFO'))
    # 'PATH_INFO': '/chat_test/'

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    # print('User.IP: %s' % ip)
    return ip

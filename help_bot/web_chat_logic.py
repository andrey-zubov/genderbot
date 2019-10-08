import logging
from time import perf_counter

from help_bot.models import (NeedHelp, StartMessage, ChatPositionWeb)


def chat_req_get(request):
    """ TBA """
    time_0 = perf_counter()

    if any(request.GET.values()):
        ui = str(request.GET['us_in']).strip()
        print("user_input: %s" % ui)

        ip = get_client_ip(request)
        user, user_position = find_web_user(ip)

        if user and not user_position:
            print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
            return start_chat()
        if user_position:

            print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
            return start_chat()
        else:

            print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
            return start_chat()
    else:
        logging.error("request.GET is empty!")
        return start_chat()


def start_chat():
    """ TBA """
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes]
    print("btn_text: %s" % btn_text)
    btn = '|'.join(btn_text)
    text = StartMessage.objects.get().text

    return "%s#####%s" % (btn, text)


def find_web_user(_ip):
    try:
        chat_web_all = ChatPositionWeb.objects.all().values()
        for w in chat_web_all:
            if w['ip_address'] == _ip:
                return 1, w['position']
        return None, 0  # user, user_position
    except Exception as ex:
        logging.error("Exception in find_web_user()\n%s" % ex)
        return None, 0  # user, user_position


def get_client_ip(request):
    print("request.META: %s" % request.META)

    print("User.HTTP_COOKIE: %s" % request.META.get('HTTP_COOKIE'))
    # 'HTTP_COOKIE': 'lastpath="http://127.0.0.1:8000/log/login/";
    print("User.REMOTE_ADDR: %s" % request.META.get('REMOTE_ADDR'))
    # 'REMOTE_ADDR': '192.168.0.51'
    print("User.HTTP_HOST: %s" % request.META.get('HTTP_HOST'))
    # 'HTTP_HOST': '192.168.0.51:8000'
    print("User.HTTP_REFERER: %s" % request.META.get('HTTP_REFERER'))
    # 'HTTP_REFERER': 'http://192.168.0.51:8000/'
    print("User.HTTP_COOKIE: %s" % request.META.get('HTTP_COOKIE'))
    # 'HTTP_COOKIE': 'csrftoken=FD0o027YvhJ6eogKBVQFDMerWC8dM9uiNRmL2KVopbCs8z8ZUQukBIPE65Zsmdsz'
    print("User.CSRF_COOKIE: %s" % request.META.get('CSRF_COOKIE'))
    # 'CSRF_COOKIE': 'FD0o027YvhJ6eogKBVQFDMerWC8dM9uiNRmL2KVopbCs8z8ZUQukBIPE65Zsmdsz'
    print("User.USERNAME: %s" % request.META.get('USERNAME'))
    # 'USERNAME': 'bequite'
    print("User.USER: %s" % request.META.get('USER'))
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

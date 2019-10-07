import logging
from time import perf_counter

from help_bot.models import NeedHelp, StartMessage


def chat_req_get(request):
    """ TBA """
    time_0 = perf_counter()

    if any(request.GET.values()):
        ui = request.GET['us_in']
        print("user_input: %s" % ui)

        btn_clicked = request.GET['btn_text']
        print("btn_clicked: %s" % btn_clicked)

        data = start_chat()

        print("chat_req_get(), data: %s" % data)
        print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
        return data
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

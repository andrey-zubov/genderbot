from time import perf_counter


def chat_req_get(request):
    """ TBA """
    time_0 = perf_counter()

    ui = request.GET['us_in']
    data = "%s%s" % (ui, 'test_bot_test_bot')

    print("chat_req_get(), data: %s" % data)
    print("\tTIME chat_req_get() = %s\n" % (perf_counter() - time_0))
    return data

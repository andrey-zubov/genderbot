from time import perf_counter

from help_bot.models import (NeedHelp)

"""
Посещаемость, 
клики по видам помощи, -> today, this month, this year
кнопке «связаться с консультантом», 
переходы (откуда пришли пользователи).
"""


def get_chat_statistic():
    print("get_chat_statistic()")
    time_0 = perf_counter()
    nh_all = NeedHelp.objects.all()
    nh_all_len = len(nh_all)

    # statistic_web
    count_web_sum = sum([i.statistic_web.count for i in nh_all])

    # statistic_telegram
    count_tel_sum = sum([i.statistic_telegram.count for i in nh_all])

    # send
    response = {
        "nh_all": nh_all,
        "nh_all_len": nh_all_len,
        "count_web_sum": count_web_sum,
        "count_tel_sum": count_tel_sum,
    }
    print("get_chat_statistic() - OK; TIME: %s" % (perf_counter() - time_0))
    return response


def save_web_chat_statistic(_user_position):
    st_web = NeedHelp.objects.get(id=_user_position).statistic_web
    # st_web = StatisticWeb.objects.get(id=_user_position)
    st_web.count += 1
    st_web.save()


def save_telegram_chat_statistic(_user_position):
    st_web = NeedHelp.objects.get(id=_user_position).statistic_telegram
    # st_web = StatisticTelegram.objects.get(id=_us_pos)
    st_web.count += 1
    st_web.save()

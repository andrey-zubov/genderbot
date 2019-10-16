from datetime import date
from time import perf_counter

from django.db import models

from help_bot.models import (NeedHelp, StatisticWeb, StatisticTelegram, StatisticAttendance)

"""
Посещаемость, -> today, this month, this year?
клики по видам помощи, кнопке «связаться с консультантом», # БЕЗ привязки ко времени
переходы (откуда пришли пользователи).
"""


def get_chat_statistic():
    print("get_chat_statistic()")
    time_0 = perf_counter()
    # all
    nh_all = NeedHelp.objects.all()
    nh_all_len = nh_all.count()
    # statistic_web
    # count_web_sum = sum([i.count for i in StatisticWeb.objects.all()])    # 0.0028670340007010964
    count_web_sum = StatisticWeb.objects.all().aggregate(models.Sum('count'))['count__sum']  # 0.0004948630003127619
    # statistic_telegram
    count_tel_sum = StatisticTelegram.objects.all().aggregate(models.Sum('count'))['count__sum']
    #
    attendance = StatisticAttendance.objects.all()
    # send
    response = {
        "nodes": nh_all,
        "nh_all_len": nh_all_len,
        "count_web_sum": count_web_sum,
        "count_tel_sum": count_tel_sum,
    }
    print("get_chat_statistic() - OK; TIME: %s" % (perf_counter() - time_0))
    return response


def save_web_chat_statistic(_user_position):
    st_web = NeedHelp.objects.get(id=_user_position).statistic_web
    st_web.count += 1
    st_web.save()

    if_today = StatisticAttendance.objects.filter(date_point__day=date.today().day)
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].web_chat_count += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(web_chat_count=1)
        st_a.save()


def save_telegram_chat_statistic(_user_position):
    st_tel = NeedHelp.objects.get(id=_user_position).statistic_telegram
    st_tel.count += 1
    st_tel.save()

    if_today = StatisticAttendance.objects.filter(date_point__day=date.today().day)
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].telegram_chat_count += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(telegram_chat_count=1)
        st_a.save()


def save_site_statistic():
    if_today = StatisticAttendance.objects.filter(date_point__day=date.today().day)
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].site_open += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(site_open=1)
        st_a.save()

from datetime import date

from django.db import models

from help_bot.models import (NeedHelp, StatisticWeb, StatisticTelegram, StatisticAttendance)
from help_bot.utility import try_except


@try_except
def get_chat_statistic():
    # all
    nh_all = NeedHelp.objects.all()
    nh_all_len = nh_all.count()

    # statistic_web
    # count_web_sum = sum([i.count for i in StatisticWeb.objects.all()])    # 0.0028670340007010964
    count_web_sum = StatisticWeb.objects.all().aggregate(models.Sum('count'))['count__sum']  # 0.0004948630003127619

    # statistic_telegram
    count_tel_sum = StatisticTelegram.objects.all().aggregate(models.Sum('count'))['count__sum']

    # Statistic Attendance
    attendance = StatisticAttendance.objects.all()
    site_open_sum = attendance.aggregate(models.Sum('site_open'))['site_open__sum']

    # today
    stats_day_all = attendance.filter(date_point=date.today())
    if stats_day_all:
        stats_day = stats_day_all[0]
    else:
        stats_day = {
            "web_chat_count": 0,
            "telegram_chat_count": 0,
            "site_open": 0,
        }

    # this month
    stats_month_all = attendance.filter(date_point__month=date.today().month, date_point__year=date.today().year)
    stats_month = {  # if stats_month_all = [] -> sum([]) = 0
        "web_chat": sum([i.web_chat_count for i in stats_month_all]),
        "telegram_chat": sum([i.telegram_chat_count for i in stats_month_all]),
        "site_open": sum([i.site_open for i in stats_month_all]),
    }

    # this year
    stats_year_all = attendance.filter(date_point__year=date.today().year)
    stats_year = {  # if stats_year_all = [] -> sum([]) = 0
        "web_chat": sum([i.web_chat_count for i in stats_year_all]),
        "telegram_chat": sum([i.telegram_chat_count for i in stats_year_all]),
        "site_open": sum([i.site_open for i in stats_year_all]),
    }

    """ graphics: 3 lists of data for every month. """
    graphics_web = []
    graphics_tel = []
    graphics_site = []
    for i in range(1, 13):  # 12 month; if attendance.filter() = [] -> sum([]) = 0
        graphics_web.append(sum([i.web_chat_count for i in attendance.filter(date_point__month=i)]))
        graphics_tel.append(sum([i.telegram_chat_count for i in attendance.filter(date_point__month=i)]))
        graphics_site.append(sum([i.site_open for i in attendance.filter(date_point__month=i)]))

    # send
    response = {
        "nodes": nh_all,  # for {% load mptt_tags %} {% recursetree my_data.nodes %}
        "nh_all_len": nh_all_len,
        "count_web_sum": count_web_sum,
        "count_tel_sum": count_tel_sum,
        "site_open_sum": site_open_sum,
        "stats_day": stats_day,
        "stats_month": stats_month,
        "stats_year": stats_year,
        "graphics_web": graphics_web,
        "graphics_tel": graphics_tel,
        "graphics_site": graphics_site,
    }
    return response


@try_except
def save_web_chat_statistic(_user_position):
    st_web = NeedHelp.objects.get(id=_user_position).statistic_web
    st_web.count += 1
    st_web.save()

    if_today = StatisticAttendance.objects.filter(date_point=date.today())  # .get(None) -> Exception
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].web_chat_count += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(web_chat_count=1)
        st_a.save()


@try_except
def save_telegram_chat_statistic(_user_position):
    st_tel = NeedHelp.objects.get(id=_user_position).statistic_telegram
    st_tel.count += 1
    st_tel.save()

    if_today = StatisticAttendance.objects.filter(date_point=date.today())  # .get(None) -> Exception
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].telegram_chat_count += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(telegram_chat_count=1)
        st_a.save()


@try_except
def save_site_statistic():
    if_today = StatisticAttendance.objects.filter(date_point=date.today())  # .get(None) -> Exception
    if if_today:  # <QuerySet [<StatisticAttendance: StatisticAttendance object (4)>]>
        if_today[0].site_open += 1
        if_today[0].save()
    else:
        st_a = StatisticAttendance(site_open=1)
        st_a.save()

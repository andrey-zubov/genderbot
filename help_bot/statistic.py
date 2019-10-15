from help_bot.models import (NeedHelp)


def get_statistic_web_chat():
    nh_all = NeedHelp.objects.all()
    nh_all_len = len(nh_all)

    response = {
        "nh_all_len": nh_all_len,
    }

    return response
